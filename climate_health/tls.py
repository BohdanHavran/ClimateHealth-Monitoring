"""Fail-closed MySQL TLS settings; no network calls or credential logging."""

import os
import ssl
from pathlib import Path

RDS_CA = (
    Path(__file__).resolve().parents[1] / "infrastructure/certificates/rds-us-east-1-bundle.crt"
)


class DatabaseTLSConfigurationError(ValueError):
    pass


class DatabaseTLSVerificationError(ConnectionError):
    pass


def mysql_tls_options(host, environ=None):
    env = os.environ if environ is None else environ
    aws = env.get("CLIMATE_ENV", "local") == "aws" or host.lower().endswith(
        (".rds.amazonaws.com", ".rds.amazonaws.com.cn")
    )
    mode = env.get("DB_TLS_MODE", "verify_identity" if aws else "disabled")
    if mode == "disabled" and not aws:
        return {"ssl_disabled": True}
    if mode != "verify_identity":
        raise DatabaseTLSConfigurationError(
            "DB_TLS_MODE must verify certificate and hostname in AWS"
        )
    ca = env.get("DB_TLS_CA_FILE") or str(RDS_CA)
    try:
        context = ssl.create_default_context(cafile=ca)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True
    except (OSError, ssl.SSLError, ValueError) as exc:
        raise DatabaseTLSConfigurationError(
            "DB_TLS_CA_FILE must contain a readable trusted CA bundle"
        ) from exc
    return {"ssl": context}
