import os
import sys
import io
import base64
import zipfile
import math
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import requests

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, jsonify, g
from werkzeug.exceptions import HTTPException
import pymysql  # Replaced mysql.connector with pymysql
import time

from climate_health.config import get_db_password
from climate_health.validation import finite_number, bounded_integer
from climate_health.fuzzy import build_fis_system, new_fis_sim, clamp_inputs, compute_hri
from climate_health.rate_limit import WindowLimiter
from climate_health.weather import CachedWeatherProvider


# =========================
# App + DB
# =========================

app = Flask(__name__)
app.config.update(MAX_CONTENT_LENGTH=262144, DATABASE_WRITES_ENABLED=False)
legacy_weather_limiter = WindowLimiter(20, 60)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "climate_app")
DB_NAME = os.getenv("DB_NAME", "climate_db")




def get_db():
    if 'db' not in g:
        password = get_db_password()
        port = bounded_integer(os.getenv('DB_PORT', '3306'), 'DB_PORT', 1, 65535)
        g.db = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=password,
            db=DB_NAME,
            port=port,
            autocommit=False,
            connect_timeout=3,
            read_timeout=5,
            write_timeout=5,
        )
        if not app.config["DATABASE_WRITES_ENABLED"]:
            with g.db.cursor() as cursor:
                cursor.execute("START TRANSACTION READ ONLY")
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def get_cursor(dictionary=False):
    db = get_db()
    if dictionary:
        return db.cursor(pymysql.cursors.DictCursor)
    return db.cursor()

def require_database_writes():
    if not app.config["DATABASE_WRITES_ENABLED"]:
        raise PermissionError("Database writes require separate authorization")


def commit():
    require_database_writes()
    db = get_db()
    db.commit()

def rollback():
    db = g.get('db')
    if db is not None:
        try:
            db.rollback()
        except Exception:
            app.logger.error('Database rollback failed')





# No need for ensure_db_connection or _db_ping, as per-request connection handles staleness

# =========================
# Helpers: JSON safe
# =========================

def to_jsonable(v):
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, np.ndarray):
        return v.tolist()
    return v


# =========================
# Tables: HRI impacts
# =========================


def seed_hri_impacts():
    require_database_writes()
    """
    Викликати один раз (або повторно — INSERT IGNORE не продублює)
    """

    impacts = {
        'low': {
            'impact': "Низький ризик: Мінімальний вплив на здоров'я. Нормальні умови для активності.",
            'recommendations': "Пийте достатньо води, носіть комфортний одяг. Моніторте зміни погоди.",
            'diseases': "Мінімальний ризик загострення хронічних захворювань (серцево-судинні, респіраторні)."
        },
        'medium': {
            'impact': "Помірний ризик: Збільшується навантаження на організм, можлива втома та дискомфорт.",
            'recommendations': "Уникайте інтенсивних навантажень у пік спеки, використовуйте сонцезахист, слідкуйте за гідратацією.",
            'diseases': "Можливе загострення астми, серцевих проблем, алергій; підвищений ризик зневоднення."
        },
        'high': {
            'impact': "Високий ризик: Серйозне навантаження, можливий тепловий стрес.",
            'recommendations': "Залишайтеся в прохолодному приміщенні, пийте багато води, уникайте сонця. За симптомів зверніться до лікаря.",
            'diseases': "Тепловий удар, ризики для серцево-судинної системи, проблеми з диханням, ниркові ускладнення."
        }
    }

    cur = get_cursor()
    for level, data in impacts.items():
        cur.execute("""
            INSERT IGNORE INTO hri_impacts (level, impact, recommendations, diseases)
            VALUES (%s, %s, %s, %s)
        """, (level, data['impact'], data['recommendations'], data['diseases']))
    commit()

def get_hri_impact(hri_value: float):

    if hri_value <= 0.30:
        level = "low"
    elif hri_value <= 0.70:
        level = "medium"
    else:
        level = "high"

    cur = get_cursor()
    cur.execute("SELECT impact, recommendations, diseases FROM hri_impacts WHERE level=%s", (level,))
    row = cur.fetchone()
    if row:
        return row[0], row[1], row[2]
    return "Невідомий рівень", "Немає рекомендацій", "Немає даних про хвороби"


# =========================
# Tables: UA places + HRI cache
# =========================



def get_cached_hri(lat, lon, ttl_minutes=30):

    cur = get_cursor()
    cur.execute(
        "SELECT fetched_at, avg_temp, solar, humidity, hri FROM hri_cache WHERE lat=%s AND lon=%s",
        (lat, lon)
    )
    row = cur.fetchone()
    if not row:
        return None

    fetched_at = row[0]
    if fetched_at < (datetime.utcnow() - timedelta(minutes=ttl_minutes)):
        return None

    return {"avg_temp": float(row[1]), "solar": float(row[2]), "humidity": float(row[3]), "hri": float(row[4])}

def put_cached_hri(lat, lon, avg_temp, solar, humidity, hri_value):
    if not app.config["DATABASE_WRITES_ENABLED"]:
        return False

    cur = get_cursor()
    cur.execute("""
      INSERT INTO hri_cache (lat, lon, fetched_at, avg_temp, solar, humidity, hri)
      VALUES (%s,%s,%s,%s,%s,%s,%s)
      ON DUPLICATE KEY UPDATE
        fetched_at=VALUES(fetched_at),
        avg_temp=VALUES(avg_temp),
        solar=VALUES(solar),
        humidity=VALUES(humidity),
        hri=VALUES(hri)
    """, (lat, lon, datetime.utcnow(), float(avg_temp), float(solar), float(humidity), float(hri_value)))
    commit()


# =========================
# Import UA places from GeoNames
# =========================

GEONAMES_UA_ZIP = "https://download.geonames.org/export/dump/UA.zip"
GEONAMES_CITIES5000_ZIP = "https://download.geonames.org/export/dump/cities5000.zip"

def import_ua_places(min_population=0, only_feature_class="P"):
    require_database_writes()
    """
    Якщо min_population >= 5000 — беремо cities5000.zip і фільтруємо country=UA.
    Інакше — беремо UA.zip.
    """


    url = GEONAMES_CITIES5000_ZIP if int(min_population) >= 5000 else GEONAMES_UA_ZIP

    r = requests.get(url, timeout=90)
    r.raise_for_status()

    zdata = io.BytesIO(r.content)
    with zipfile.ZipFile(zdata) as zf:
        names = zf.namelist()

        # Явно вибираємо правильний txt
        if url == GEONAMES_UA_ZIP:
            txt_name = "UA.txt" if "UA.txt" in names else next((n for n in names if n.lower().endswith(".txt")), None)
        else:
            txt_name = "cities5000.txt" if "cities5000.txt" in names else next((n for n in names if n.lower().endswith(".txt")), None)

        if not txt_name:
            raise RuntimeError(f"Не знайшов .txt у {url}. Всередині: {names[:10]}")

        lines = zf.open(txt_name).read().decode("utf-8", errors="replace").splitlines()

    insert_sql = """
    INSERT INTO ua_places
      (geoname_id, name, asciiname, latitude, longitude, feature_class, feature_code,
       admin1_code, admin2_code, population, timezone, modified_date)
    VALUES
      (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
      name=VALUES(name),
      asciiname=VALUES(asciiname),
      latitude=VALUES(latitude),
      longitude=VALUES(longitude),
      feature_class=VALUES(feature_class),
      feature_code=VALUES(feature_code),
      admin1_code=VALUES(admin1_code),
      admin2_code=VALUES(admin2_code),
      population=VALUES(population),
      timezone=VALUES(timezone),
      modified_date=VALUES(modified_date)
    """

    cur = get_cursor()
    batch = []
    count = 0

    # Діагностика (щоб одразу бачити де “обнулилось”)
    total = ok19 = ua = fclass_ok = pop_ok = 0

    for line in lines:
        if not line.strip():
            continue
        total += 1

        parts = line.split("\t")
        if len(parts) < 19:
            continue
        ok19 += 1

        country = parts[8]
        if country != "UA":
            continue
        ua += 1

        fclass = parts[6] or None
        if only_feature_class and fclass != only_feature_class:
            continue
        fclass_ok += 1

        population = int(parts[14] or 0)
        if population < int(min_population):
            continue
        pop_ok += 1

        geoname_id = int(parts[0])
        name_ = parts[1]
        asciiname = parts[2] or None
        lat = float(parts[4])
        lon = float(parts[5])
        fcode = parts[7] or None
        admin1 = parts[10] or None
        admin2 = parts[11] or None
        timezone = parts[17] or None
        mdate = parts[18] or None

        batch.append((geoname_id, name_, asciiname, lat, lon, fclass, fcode, admin1, admin2, population, timezone, mdate))

        if len(batch) >= 2000:
            cur.executemany(insert_sql, batch)
            commit()
            count += len(batch)
            batch.clear()

    if batch:
        cur.executemany(insert_sql, batch)
        commit()
        count += len(batch)

    print(f"[import debug] source={url}")
    print(f"[import debug] total={total}, ok19={ok19}, countryUA={ua}, fclassOK={fclass_ok}, popOK={pop_ok}")
    return count


# =========================
# Fuzzy system (без "дір" на межах)
# =========================








# =========================
# Weather API
# =========================

API_KEY = os.getenv("OPENWEATHER_API_KEY")

weather_provider = CachedWeatherProvider(lambda: API_KEY)

def get_current_weather(city: str):
    return weather_provider.city(city)

def get_current_weather_by_coords(lat: float, lon: float):
    return weather_provider.coordinates(lat, lon)

@app.before_request
def limit_legacy_weather_requests():
    expensive = request.path in {'/api/hri_at', '/api/analyze'}
    if expensive and not legacy_weather_limiter.allow(request.remote_addr or 'unknown'):
        return jsonify(error='Перевищено ліміт запитів'), 429, {'Retry-After': '60'}


# =========================
# Plots for analyze
# =========================

def generate_plots(results):
    df = pd.DataFrame(results)

    # графік HRI
    fig1, ax1 = plt.subplots()
    ax1.plot(df["month"], df["hri"], marker="o", linestyle="-")
    ax1.set_title("HRI")
    ax1.set_xlabel("Місяць/режим")
    ax1.set_ylabel("HRI")
    ax1.grid(True)
    buf1 = io.BytesIO()
    fig1.savefig(buf1, format="png", bbox_inches="tight")
    buf1.seek(0)
    plot1 = base64.b64encode(buf1.read()).decode("utf-8")

    # графік критеріїв (якщо є)
    fig2, ax2 = plt.subplots()
    exclude = {"month", "hri", "impact", "recommendations", "diseases"}
    cols = [c for c in df.columns if c not in exclude]
    if cols:
        df_plot = df[["month"] + cols].copy()
        df_plot.set_index("month").plot(kind="bar", ax=ax2)
        ax2.set_title("Критерії")
        ax2.set_xlabel("Місяць/режим")
        ax2.grid(True)
    buf2 = io.BytesIO()
    fig2.savefig(buf2, format="png", bbox_inches="tight")
    buf2.seek(0)
    plot2 = base64.b64encode(buf2.read()).decode("utf-8")

    plt.close(fig1)
    plt.close(fig2)
    return plot1, plot2


# =========================
# Pages
# =========================

@app.get('/health/live')
def liveness():
    return jsonify(status='ok')


@app.get('/health/ready')
def readiness():
    try:
        with get_db().cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        return jsonify(status='ok', database='available')
    except Exception:
        app.logger.warning('Readiness check failed: database unavailable')
        return jsonify(status='unavailable', database='unavailable'), 503


@app.route("/")
def home():
    return render_template("info.html")

@app.route("/info")
def info():
    return render_template("info.html")

@app.route("/start")
def start():
    return render_template("index.html")

@app.route("/analyze", methods=["GET"])
def analyze():
    years = [2020, 2021, 2022, 2023, 2024]
    return render_template("analyze.html", years=years)

@app.route("/map", methods=["GET"])
def map_page():
    return render_template("map.html")


# =========================
# API: analyze
# =========================

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    criteria = request.form.getlist("criteria")
    mode = request.form.get("mode", "db")

    year = request.form.get("year")
    month = request.form.get("month")

    manual_temp = request.form.get("manual_temp", "")
    manual_solar = request.form.get("manual_solar", "")
    manual_humidity = request.form.get("manual_humidity", "")

    api_city = request.form.get("api_city")

    neutrals = {"avg_temp": 12.5, "solar": 180.0, "humidity": 65.0}
    param_map = {"temp": "avg_temp", "solar": "solar", "humidity": "humidity"}
    display_map = {"temp": "Температура (°C)", "solar": "Сонячна радіація (W/m²)", "humidity": "Вологість (%)"}

    if mode not in {'manual', 'api', 'db'} or any(c not in param_map for c in criteria):
        return jsonify(error='Невідомий режим або критерій'), 400
    try:
        if mode == 'manual':
            for name, value, low, high in (
                ('manual_temp', manual_temp, -100, 70),
                ('manual_solar', manual_solar, 0, 1600),
                ('manual_humidity', manual_humidity, 0, 100),
            ):
                if value != '':
                    finite_number(value, name, low, high)
        if mode == 'db':
            bounded_integer(year, 'year', 1800, 2200)
            if month:
                bounded_integer(month, 'month', 1, 12)
        if mode == 'api':
            if not api_city or not api_city.strip() or len(api_city.strip()) > 100:
                raise ValueError('Вкажіть назву міста до 100 символів')
            api_city = api_city.strip()
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    # якщо нічого не вибрано — беремо все (щоб не “залипав” ~0.5 на нейтралях)
    if not criteria:
        criteria = ["temp", "solar", "humidity"]
    selected_keys = [param_map[c] for c in criteria]

    results = []

    try:
        if mode == "manual":
            inputs = {
                "avg_temp": float(manual_temp) if manual_temp != "" else neutrals["avg_temp"],
                "solar": float(manual_solar) if manual_solar != "" else neutrals["solar"],
                "humidity": float(manual_humidity) if manual_humidity != "" else neutrals["humidity"],
            }
            inputs = clamp_inputs(inputs)

            # те, що не вибрано — ставимо нейтраль
            for k in list(inputs.keys()):
                if k not in selected_keys:
                    inputs[k] = neutrals[k]

            hri_value = compute_hri(inputs)
            impact, recommendations, diseases = get_hri_impact(hri_value)

            row = {
                "month": "Ручний ввід",
                "hri": round(hri_value, 3),
                "impact": impact,
                "recommendations": recommendations,
                "diseases": diseases
            }
            for c in criteria:
                row[display_map[c]] = float(inputs[param_map[c]])
            results.append(row)

        elif mode == "api":
            if not api_city:
                return jsonify({"error": "Вкажіть місто"}), 400

            w = get_current_weather(api_city)
            if not w:
                return jsonify({"error": "Помилка отримання даних з API (перевірте місто/API ключ)"}), 400

            inputs = clamp_inputs(w)
            for k in list(inputs.keys()):
                if k not in selected_keys:
                    inputs[k] = neutrals[k]

            hri_value = compute_hri(inputs)
            impact, recommendations, diseases = get_hri_impact(hri_value)

            row = {
                "month": "Поточний день (API)",
                "hri": round(hri_value, 3),
                "impact": impact,
                "recommendations": recommendations,
                "diseases": diseases
            }
            for c in criteria:
                row[display_map[c]] = float(inputs[param_map[c]])
            results.append(row)

        else:
            # режим DB
            if not year:
                return jsonify({"error": "Вкажіть рік"}), 400

            # NOTE: припускаю, що в тебе є таблиця climate_data з колонками:
            # (id, year, month, avg_temp, solar_irradiance, humidity)
            cur = get_cursor()
            if month:
                cur.execute("SELECT year, month, avg_temp, solar_irradiance, humidity FROM climate_data WHERE year=%s AND month=%s",
                            (year, month))
            else:
                cur.execute("SELECT year, month, avg_temp, solar_irradiance, humidity FROM climate_data WHERE year=%s ORDER BY month",
                            (year,))

            rows = cur.fetchall()
            if not rows:
                return jsonify({"error": "Дані відсутні"}), 404

            for r in rows:
                # r: (year, month, avg_temp, solar_irradiance, humidity)
                inputs = {
                    "avg_temp": float(r[2]) if r[2] is not None else neutrals["avg_temp"],
                    "solar": float(r[3]) if r[3] is not None else neutrals["solar"],
                    "humidity": float(r[4]) if r[4] is not None else neutrals["humidity"],
                }
                inputs = clamp_inputs(inputs)
                for k in list(inputs.keys()):
                    if k not in selected_keys:
                        inputs[k] = neutrals[k]

                hri_value = compute_hri(inputs)
                impact, recommendations, diseases = get_hri_impact(hri_value)

                row = {
                    "month": int(r[1]),
                    "hri": round(hri_value, 3),
                    "impact": impact,
                    "recommendations": recommendations,
                    "diseases": diseases
                }
                for c in criteria:
                    row[display_map[c]] = float(inputs[param_map[c]])
                results.append(row)

        plot1, plot2 = generate_plots(results)
        clean_results = [{k: to_jsonable(v) for k, v in r.items()} for r in results]
        return jsonify({"results": clean_results, "plot_hri": plot1, "plot_criteria": plot2})

    except Exception:
        rollback()
        app.logger.error('Analysis failed due to unavailable dependency or invalid source data')
        return jsonify(error='Не вдалося виконати аналіз: перевірте доступність даних'), 503


# =========================
# API: map (DB places + HRI by click)
# =========================

@app.route("/api/places_in_bounds", methods=["GET"])
def api_places_in_bounds():
    try:
        minLat = finite_number(request.args.get("minLat"), 'minLat', -90, 90)
        maxLat = finite_number(request.args.get("maxLat"), 'maxLat', -90, 90)
        minLon = finite_number(request.args.get("minLon"), 'minLon', -180, 180)
        maxLon = finite_number(request.args.get("maxLon"), 'maxLon', -180, 180)
        zoom = bounded_integer(request.args.get("zoom", 6), 'zoom', 0, 22)
        limit = bounded_integer(request.args.get("limit", 1200), 'limit', 1, 5000)
        if minLat > maxLat or minLon > maxLon:
            raise ValueError('Некоректні межі карти')
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    try:
    

        # чим менший zoom — тим більший pop-фільтр (менше точок)
        if zoom <= 6:
            min_pop = 50000
        elif zoom == 7:
            min_pop = 20000
        elif zoom == 8:
            min_pop = 5000
        elif zoom == 9:
            min_pop = 1000
        else:
            min_pop = 0

        cur = get_cursor(dictionary=True)
        cur.execute("""
          SELECT geoname_id, name, latitude, longitude, population
          FROM ua_places
          WHERE latitude BETWEEN %s AND %s
            AND longitude BETWEEN %s AND %s
            AND population >= %s
          ORDER BY population DESC
          LIMIT %s
        """, (minLat, maxLat, minLon, maxLon, min_pop, limit))

        rows = cur.fetchall()
        out = [{
            "id": int(r["geoname_id"]),
            "name": r["name"],
            "lat": float(r["latitude"]),
            "lon": float(r["longitude"]),
            "population": int(r["population"] or 0),
        } for r in rows]

        return jsonify({"places": out})

    except Exception:
        app.logger.error('Place lookup failed due to unavailable dependency')
        return jsonify(error='Дані населених пунктів недоступні'), 503


@app.route("/api/hri_at", methods=["GET"])
def api_hri_at():
    try:
        lat = finite_number(request.args.get("lat"), 'lat', -90, 90)
        lon = finite_number(request.args.get("lon"), 'lon', -180, 180)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    try:

        # ключ кешу (не робимо мільйон ключів через дрібні відхилення)
        k_lat = round(lat, 4)
        k_lon = round(lon, 4)

        cached = get_cached_hri(k_lat, k_lon, ttl_minutes=30)
        if cached:
            hri_value = finite_number(cached["hri"], 'cached_hri', 0, 1)
            cached_temp = finite_number(cached["avg_temp"], 'cached_temperature', -100, 70)
            cached_solar = finite_number(cached["solar"], 'cached_solar', 0, 1600)
            cached_humidity = finite_number(cached["humidity"], 'cached_humidity', 0, 100)
            impact, recommendations, diseases = get_hri_impact(hri_value)
            level = "low" if hri_value <= 0.30 else "medium" if hri_value <= 0.70 else "high"

            return jsonify({
                "lat": k_lat, "lon": k_lon,
                "avg_temp": cached_temp,
                "solar": cached_solar,
                "humidity": cached_humidity,
                "hri": float(round(hri_value, 3)),
                "level": level,
                "impact": impact,
                "recommendations": recommendations,
                "diseases": diseases,
                "cached": True
            })

        w = get_current_weather_by_coords(lat, lon)
        if not w:
            return jsonify({"error": "Не вдалося отримати дані погоди"}), 400

        inputs = clamp_inputs({"avg_temp": w["avg_temp"], "solar": w["solar"], "humidity": w["humidity"]})
        hri_value = compute_hri(inputs)

        put_cached_hri(k_lat, k_lon, inputs["avg_temp"], inputs["solar"], inputs["humidity"], hri_value)

        impact, recommendations, diseases = get_hri_impact(hri_value)
        level = "low" if hri_value <= 0.30 else "medium" if hri_value <= 0.70 else "high"

        return jsonify({
            "lat": k_lat, "lon": k_lon,
            "avg_temp": float(inputs["avg_temp"]),
            "solar": float(inputs["solar"]),
            "humidity": float(inputs["humidity"]),
            "hri": float(round(hri_value, 3)),
            "level": level,
            "impact": impact,
            "recommendations": recommendations,
            "diseases": diseases,
            "cached": False
        })

    except Exception:
        app.logger.error('HRI lookup failed due to unavailable dependency or invalid source data')
        return jsonify(error='Оцінка HRI недоступна'), 503


# =========================
# Main / CLI
# =========================

from climate_health.api import create_api
app.register_blueprint(create_api(get_db, weather_provider))


@app.errorhandler(HTTPException)
def scoped_http_error(error):
    if request.path.startswith('/api/v1/'):
        return jsonify(error={'code':'http_error', 'message':'Некоректний HTTP-запит'}), error.code
    return error


if __name__ == "__main__":
    # приклад:
    #   python climat.py import_ua_places 0
    #   python climat.py import_ua_places 5000
    if len(sys.argv) > 1 and sys.argv[1] == "import_ua_places":
        mp = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        try:
            count = import_ua_places(min_population=mp)
            print(f"Imported/updated rows: {count}")
        except Exception as e:
            print(f"Import failed: {e}")
            sys.exit(1)
        sys.exit(0)

    # опціонально (1 раз):
    # seed_hri_impacts()

    app.run(debug=False, host=os.getenv('APP_HOST', '127.0.0.1'))
