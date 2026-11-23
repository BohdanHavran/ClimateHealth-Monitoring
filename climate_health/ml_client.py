"""Backend-to-ML boundary. Phase 2 intentionally accepts no available prediction."""

from urllib.parse import urlsplit

import requests

from ml_contract import evaluate_unavailable_request


class MLClient:
    def __init__(self, url=None, token=None, transport=requests.post):
        self.url, self.token, self.transport = url, token, transport

    def predict(self, payload):
        unavailable = evaluate_unavailable_request(payload)
        if payload["feature_schema_version"] != "climate-v1":
            raise ValueError("Непідтримувана версія ознак")
        if not self.url or not self.token:
            return dict(unavailable, reason="service_not_configured")
        parsed = urlsplit(self.url)
        # Local phase only. Non-loopback services need a reviewed TLS/auth configuration.
        if (
            parsed.scheme != "http"
            or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in {"", "/"}
        ):
            return dict(unavailable, reason="service_configuration_invalid")
        try:
            response = self.transport(
                self.url.rstrip("/") + "/api/v1/predict",
                json=payload,
                headers={"Authorization": "Bearer " + self.token},
                timeout=(2, 5),
                allow_redirects=False,
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
        except requests.Timeout:
            return dict(unavailable, reason="service_timeout")
        except (requests.RequestException, ValueError):
            return dict(unavailable, reason="service_unavailable")
