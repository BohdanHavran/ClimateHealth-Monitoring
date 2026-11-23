"""Development server with an explicit, allowlisted local .env loader."""
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"DB_HOST", "DB_PORT", "DB_USER", "DB_NAME", "DB_PASS", "DB_PASS_FILE",
           "OPENWEATHER_API_KEY", "PORT", "ML_SERVICE_URL", "ML_SERVICE_TOKEN"}
local_env = ROOT / ".env"
if local_env.exists():
    for line in local_env.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if key in ALLOWED and key not in os.environ:
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            os.environ[key] = value
if os.environ.get("DB_PASS_FILE"):
    secret_path = Path(os.environ["DB_PASS_FILE"])
    if not secret_path.is_absolute():
        os.environ["DB_PASS_FILE"] = str(ROOT / secret_path)
sys.path.insert(0, str(ROOT))
from climat import app  # noqa: E402

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "8000")),
            debug=False, use_reloader=False)
