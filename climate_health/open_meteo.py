"""Non-commercial Open-Meteo model data with explicit source, time and units."""

from collections import OrderedDict
from datetime import datetime, timezone
from threading import Lock
from time import monotonic

import requests

from .rate_limit import WindowLimiter
from .validation import finite_number


class OpenMeteoProvider:
    def __init__(self, transport=requests.get, clock=monotonic):
        self.transport, self.clock = transport, clock
        self.cache, self.lock = OrderedDict(), Lock()
        self.quota = WindowLimiter(30, 60, clock=clock)
        self.daily_quota = WindowLimiter(9000, 86400, clock=clock)

    def coordinates(self, lat, lon):
        lat = round(finite_number(lat, "lat", -90, 90), 4)
        lon = round(finite_number(lon, "lon", -180, 180), 4)
        key = (lat, lon)
        with self.lock:
            cached = self.cache.get(key)
            if cached and self.clock() - cached[0] < 300:
                return dict(cached[1], cached=True)
            if not self.quota.allow("provider") or not self.daily_quota.allow("provider"):
                raise RuntimeError("Weather quota exceeded")
            response = self.transport(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,shortwave_radiation",
                    "timezone": "UTC",
                },
                timeout=(3, 7),
                allow_redirects=False,
            )
            if response.status_code != 200:
                raise RuntimeError("Weather provider unavailable")
            payload = response.json()
            current, units = payload["current"], payload["current_units"]
            if (
                units.get("temperature_2m") != "°C"
                or units.get("relative_humidity_2m") != "%"
                or units.get("shortwave_radiation") != "W/m²"
            ):
                raise RuntimeError("Unexpected weather units")
            when = datetime.fromisoformat(current["time"].replace("Z", "+00:00"))
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)  # API explicitly requested timezone=UTC
            now = datetime.now(timezone.utc)
            result = {
                "avg_temp": finite_number(current["temperature_2m"], "temperature", -100, 70),
                "humidity": finite_number(current["relative_humidity_2m"], "humidity", 0, 100),
                "solar": finite_number(current["shortwave_radiation"], "solar", 0, 1600),
                "lat": lat,
                "lon": lon,
                "source": "Open-Meteo",
                "data_time": when.astimezone(timezone.utc).isoformat(),
                "fetched_at": now.isoformat(),
                "cached": False,
                "data_kind": "model_current_conditions",
                "solar_method": "model_shortwave_radiation",
                "quality_issues": [
                    "conditions:model_not_station_observation",
                ],
            }
            if abs((now - when).total_seconds()) > 3600:
                result["quality_issues"].append("data_time:stale")
            self.cache[key] = (self.clock(), result)
            self.cache.move_to_end(key)
            if len(self.cache) > 256:
                self.cache.popitem(last=False)
            return dict(result)
