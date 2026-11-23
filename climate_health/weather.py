"""OpenWeather adapter: bounded TTL cache, single-flight lock, global quota."""

from collections import OrderedDict
from threading import Lock
from time import monotonic

import requests

from .rate_limit import WindowLimiter
from .validation import finite_number


class CachedWeatherProvider:
    def __init__(self, key, ttl=300, capacity=256, clock=monotonic, transport=requests.get):
        self.key, self.ttl, self.capacity, self.clock = key, ttl, capacity, clock
        self.transport, self.cache, self.lock = transport, OrderedDict(), Lock()
        self.quota = WindowLimiter(40, 60, clock=clock)

    def city(self, city):
        if not isinstance(city, str) or not city.strip() or len(city.strip()) > 100:
            raise ValueError("Некоректна назва міста")
        return self._fetch(("city", city.strip().casefold()), {"q": city.strip()})

    def coordinates(self, lat, lon):
        lat = round(finite_number(lat, "lat", -90, 90), 4)
        lon = round(finite_number(lon, "lon", -180, 180), 4)
        return self._fetch(("coordinates", lat, lon), {"lat": lat, "lon": lon})

    def _fetch(self, cache_key, params):
        # Serializes fills: concurrent identical misses do not spend duplicate requests.
        with self.lock:
            cached = self.cache.get(cache_key)
            if cached and self.clock() - cached[0] < self.ttl:
                return dict(cached[1])
            secret = self.key()
            if not secret or not self.quota.allow("provider"):
                raise RuntimeError("Weather provider unavailable or quota exceeded")
            response = self.transport(
                "https://api.openweathermap.org/data/2.5/weather",
                params={**params, "appid": secret, "units": "metric"},
                timeout=(3, 5),
            )
            if response.status_code != 200:
                raise RuntimeError("Weather provider unavailable")
            data = response.json()
            clouds = finite_number(data.get("clouds", {}).get("all", 0), "clouds", 0, 100)
            result = {
                "avg_temp": finite_number(data["main"]["temp"], "temperature", -100, 70),
                "humidity": finite_number(data["main"]["humidity"], "humidity", 0, 100),
                # Legacy approximation, not an observed irradiance value.
                "solar": 300.0 * (1.0 - clouds / 100.0),
            }
            self.cache[cache_key] = (self.clock(), result)
            self.cache.move_to_end(cache_key)
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)
            return dict(result)
