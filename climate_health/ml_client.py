"""Backend-to-ML boundary. Phase 2 intentionally accepts no available prediction."""

from urllib.parse import urlsplit
import os
import math
from pathlib import Path

import requests

from ml_contract import evaluate_unavailable_request


class MLClient:
    def __init__(
        self, url=None, token=None, transport=requests.post, *, allowed_host=None, ca_file=None
    ):
        self.url, self.token, self.transport = url, token, transport
        self.allowed_host = (
            allowed_host if allowed_host is not None else os.getenv("ML_SERVICE_ALLOWED_HOST")
        )
        self.ca_file = ca_file if ca_file is not None else os.getenv("ML_TLS_CA_FILE")

    def predict(self, payload):
        unavailable = evaluate_unavailable_request(payload)
        if payload["feature_schema_version"] != "climate-v1":
            raise ValueError("Непідтримувана версія ознак")
        if not self.url or not self.token:
            return dict(unavailable, reason="service_not_configured")
        try:
            if any(ord(c) < 33 or ord(c) == 127 for c in self.url):
                return dict(unavailable, reason="service_configuration_invalid")
            parsed = urlsplit(self.url)
            port = parsed.port
            connect = float(os.getenv("ML_CONNECT_TIMEOUT", "2"))
            read = float(os.getenv("ML_READ_TIMEOUT", "5"))
        except (ValueError, TypeError):
            return dict(unavailable, reason="service_configuration_invalid")
        local = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
        secure = parsed.scheme == "https" and parsed.hostname == self.allowed_host
        if (
            not (
                (parsed.scheme == "http" and local and os.getenv("CLIMATE_ENV", "local") != "aws")
                or secure
            )
            or (port is not None and not 1 <= port <= 65535)
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in {"", "/"}
            or not all(math.isfinite(t) and 0 < t <= 30 for t in (connect, read))
            or "\r" in self.token
            or "\n" in self.token
        ):
            return dict(unavailable, reason="service_configuration_invalid")
        verify = self.ca_file or True
        if self.ca_file and not Path(self.ca_file).is_file():
            return dict(unavailable, reason="service_configuration_invalid")
        try:
            response = self.transport(
                self.url.rstrip("/") + "/api/v1/predict",
                json=payload,
                headers={"Authorization": "Bearer " + self.token},
                timeout=(connect, read),
                allow_redirects=False,
                verify=verify,
            )
            body = response.json()
            valid = (
                response.status_code == 503
                and isinstance(body, dict)
                and set(body) == set(unavailable)
                and body.get("status") == "unavailable"
                and body.get("value") is None
                and body.get("model_version") is None
                and body.get("target") is None
                and body.get("unit") is None
                and body.get("data_quality") == "unavailable"
                and body.get("reason") == "model_unavailable"
            )
            if valid:
                # Do not trust remote timestamps/extra fields in the public response.
                return unavailable
            return dict(unavailable, reason="model_contract_mismatch")
        except requests.exceptions.SSLError:
            return dict(unavailable, reason="service_tls_failed")
        except requests.Timeout:
            return dict(unavailable, reason="service_timeout")
        except (requests.RequestException, ValueError):
            return dict(unavailable, reason="service_unavailable")
