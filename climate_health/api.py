"""Versioned JSON API. Reads MySQL; no schema creation or data writes."""

import os

from flask import Blueprint, current_app, jsonify, request
from werkzeug.exceptions import HTTPException

from .ml_client import MLClient
from .rate_limit import WindowLimiter
from .repository import ClimateRepository, schema_report
from .services import analyze_hri
from .validation import bounded_integer, finite_number
from .weather import CachedWeatherProvider


def create_api(get_connection, weather_provider=None):
    api = Blueprint("api_v1", __name__, url_prefix="/api/v1")
    limiter = WindowLimiter(60, 60)
    weather = weather_provider or CachedWeatherProvider(lambda: os.getenv("OPENWEATHER_API_KEY"))

    def success(data, **meta):
        return jsonify(data=data, meta={"api_version": "v1", **meta})

    def failure(code, message, status):
        return jsonify(error={"code": code, "message": message}), status

    @api.before_request
    def rate_limit():
        if not limiter.allow(request.remote_addr or "unknown"):
            response, status = failure("rate_limited", "Забагато запитів; повторіть пізніше", 429)
            return response, status, {"Retry-After": "60"}

    @api.errorhandler(ValueError)
    def invalid(error):
        return failure("invalid_request", str(error), 400)

    @api.errorhandler(HTTPException)
    def http_error(error):
        return failure("http_error", "Некоректний HTTP-запит", error.code)

    @api.errorhandler(Exception)
    def dependency_error(error):
        current_app.logger.warning("Versioned API dependency unavailable")
        return failure("dependency_unavailable", "Сервіс тимчасово недоступний", 503)

    @api.get("/status")
    def status():
        return success(
            {
                "status": "ok",
                "database_writes_enabled": False,
                "prediction_status": "model_unavailable",
            }
        )

    @api.get("/schema")
    def schema():
        report = schema_report(get_connection())
        if not report["compatible"]:
            return failure("schema_incompatible", "Структура БД потребує перевірки", 503)
        return success(report)

    @api.get("/observations")
    def observations():
        limit = bounded_integer(request.args.get("limit", "50"), "limit", 1, 200)
        after_id = bounded_integer(request.args.get("after_id", "0"), "after_id", 0, 2**63 - 1)
        year = request.args.get("year")
        month = request.args.get("month")
        if year is not None:
            year = bounded_integer(year, "year", 1800, 2200)
        if month is not None:
            month = bounded_integer(month, "month", 1, 12)
        rows, next_id = ClimateRepository(get_connection()).observations(
            after_id, limit, year, month
        )
        return success(
            rows,
            next_after_id=next_id,
            limit=limit,
            source="mysql:climate_data",
            geography="unspecified",
            units={"avg_temp": "degC", "solar_irradiance": "W/m2", "humidity": "%"},
        )

    @api.get("/places")
    def places():
        bounds = [
            finite_number(request.args.get(name), name, low, high)
            for name, low, high in [
                ("south", -90, 90),
                ("north", -90, 90),
                ("west", -180, 180),
                ("east", -180, 180),
            ]
        ]
        if bounds[0] > bounds[1] or bounds[2] > bounds[3]:
            raise ValueError("Некоректні межі карти")
        limit = bounded_integer(request.args.get("limit", "100"), "limit", 1, 1000)
        return success(ClimateRepository(get_connection()).places(*bounds, limit))

    @api.post("/hri")
    def hri():
        return success(analyze_hri(request.get_json()))

    @api.get("/weather")
    def current_weather():
        data = weather.city(request.args.get("city"))
        return success(
            data,
            source="OpenWeather",
            solar_method="cloud_cover_approximation",
            cache_ttl_seconds=300,
        )

    @api.post("/predictions")
    def prediction():
        payload = request.get_json()
        result = MLClient(os.getenv("ML_SERVICE_URL"), os.getenv("ML_SERVICE_TOKEN")).predict(
            payload
        )
        return jsonify(data=result, meta={"api_version": "v1"}), 503

    return api
