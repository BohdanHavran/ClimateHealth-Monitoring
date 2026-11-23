"""Parameterized read-only repositories over the existing MySQL schema."""

import math

import pymysql


EXPECTED_COLUMNS = {
    "climate_data": {"id", "year", "month", "avg_temp", "solar_irradiance", "humidity"},
    "ua_places": {"geoname_id", "name", "latitude", "longitude", "population"},
    "hri_cache": {"lat", "lon", "fetched_at", "avg_temp", "solar", "humidity", "hri"},
    "hri_impacts": {"level", "impact", "recommendations", "diseases"},
}


def schema_report(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT TABLE_NAME,COLUMN_NAME FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA=DATABASE()"
        )
        actual = {}
        for table, column in cursor.fetchall():
            actual.setdefault(table, set()).add(column)
    missing = {
        table: sorted(columns - actual.get(table, set()))
        for table, columns in EXPECTED_COLUMNS.items()
        if columns - actual.get(table, set())
    }
    return {"compatible": not missing, "missing_columns": missing}


class ClimateRepository:
    def __init__(self, connection):
        self.connection = connection

    def observations(self, after_id, limit, year=None, month=None):
        clauses, params = ["id > %s"], [after_id]
        if year is not None:
            clauses.append("year=%s")
            params.append(year)
        if month is not None:
            clauses.append("month=%s")
            params.append(month)
        sql = (
            "SELECT id,year,month,avg_temp,solar_irradiance,humidity FROM climate_data WHERE "
            + " AND ".join(clauses)
            + " ORDER BY id LIMIT %s"
        )
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, (*params, limit + 1))
            rows = cursor.fetchall()
        has_more = len(rows) > limit
        result = []
        for source in rows[:limit]:
            row, issues = dict(source), []
            for name, low, high in (
                ("avg_temp", -100, 70),
                ("solar_irradiance", 0, 1600),
                ("humidity", 0, 100),
                ("year", 1800, 2200),
                ("month", 1, 12),
            ):
                value = row.get(name)
                if value is None:
                    issues.append(name + ":missing")
                elif not math.isfinite(float(value)) or not low <= float(value) <= high:
                    row[name] = None
                    issues.append(name + ":invalid")
            row["quality_issues"] = issues
            result.append(row)
        return result, (result[-1]["id"] if has_more and result else None)

    def places(self, south, north, west, east, limit):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT geoname_id AS id,name,latitude AS lat,longitude AS lon,population "
                "FROM ua_places WHERE latitude BETWEEN %s AND %s "
                "AND longitude BETWEEN %s AND %s ORDER BY geoname_id LIMIT %s",
                (south, north, west, east, limit),
            )
            rows = list(cursor.fetchall())
        for row in rows:
            if not all(
                row.get(key) is not None
                and math.isfinite(float(row[key]))
                and low <= float(row[key]) <= high
                for key, low, high in (("lat", -90, 90), ("lon", -180, 180))
            ):
                raise RuntimeError("Invalid geographic source data")
        return rows
