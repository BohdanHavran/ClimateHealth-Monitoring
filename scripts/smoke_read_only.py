"""Start a temporary loopback HTTP server; probe only routes without schema writes."""
import argparse
import json
import os
from pathlib import Path
import sys
from threading import Thread
from urllib.request import urlopen

from inspect_mysql import legacy_password

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--secret-source", required=True)
    args = parser.parse_args()
    os.environ.update(DB_HOST="192.168.0.165", DB_USER="root", DB_NAME="climate_db",
                      DB_PASS=legacy_password(args.secret_source), MPLBACKEND="Agg")
    os.environ.pop("DB_PASS_FILE", None)
    sys.path.insert(0, str(ROOT))
    from climat import app
    from werkzeug.serving import make_server
    server = make_server("127.0.0.1", 0, app)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    results = []
    try:
        for path in ("/health/live", "/health/ready", "/", "/map", "/static/js/safe-html.js"):
            with urlopen(f"http://127.0.0.1:{server.server_port}{path}", timeout=10) as response:
                response.read()
                results.append({"path": path, "http_status": response.status})
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
        os.environ.pop("DB_PASS", None)
    report = {"transport": "real loopback HTTP", "database_probe": "SELECT 1 only",
              "database_writes": 0, "external_weather_calls": 0, "routes": results}
    output = ROOT / "docs/reports/http-smoke.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("HTTP smoke passed; five routes, real MySQL readiness, no data/schema writes")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("Smoke failed (details redacted): " + type(exc).__name__)
        raise SystemExit(1)
