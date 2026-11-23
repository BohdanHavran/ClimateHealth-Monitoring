"""Read-only MySQL metadata inspection; credentials never appear in output."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]


def legacy_password(path):
    values = {}
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.removeprefix("export ").strip()] = value
    for key in ("DB_PASS", "DB_PASSWORD", "MYSQL_PASSWORD", "MYSQL_ROOT_PASSWORD"):
        if values.get(key):
            return values[key]
    for key in ("DATABASE_URL", "SQLALCHEMY_DATABASE_URI"):
        if values.get(key):
            password = urlsplit(values[key]).password
            if password:
                return unquote(password)
    raise ValueError("No supported password field found; no values were displayed")


def inspect(host, port, secret_source):
    import pymysql
    password = legacy_password(secret_source)
    connection = pymysql.connect(
        host=host, port=port, user="root", password=password,
        connect_timeout=5, read_timeout=10, write_timeout=5,
        charset="utf8mb4", autocommit=False,
    )
    try:
        with connection.cursor() as cur:
            cur.execute("START TRANSACTION READ ONLY")
            cur.execute("SELECT VERSION(), CURRENT_USER(), USER()")
            version, account, client = cur.fetchone()
            cur.execute("SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = %s", ("climate_db",))
            schemas = [row[0] for row in cur.fetchall()]
            cur.execute("SELECT TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLUMN_KEY FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = %s ORDER BY TABLE_SCHEMA,TABLE_NAME,ORDINAL_POSITION", ("climate_db",))
            columns = [dict(zip(("schema", "table", "column", "type", "nullable", "key"), row)) for row in cur.fetchall()]
            cur.execute("SELECT TABLE_SCHEMA,TABLE_NAME,INDEX_NAME,NON_UNIQUE,SEQ_IN_INDEX,COLUMN_NAME FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = %s ORDER BY TABLE_SCHEMA,TABLE_NAME,INDEX_NAME,SEQ_IN_INDEX", ("climate_db",))
            indexes = [dict(zip(("schema", "table", "index", "non_unique", "position", "column"), row)) for row in cur.fetchall()]
        result = {"status": "connected_read_only", "server_version": version,
                  "account": account, "client": client, "schemas": schemas,
                  "columns": columns, "indexes": indexes,
                  "data_rows_read": 0, "schema_or_data_writes": 0}
    finally:
        connection.rollback()
        connection.close()
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="192.168.0.165")
    parser.add_argument("--port", type=int, default=3306)
    parser.add_argument("--secret-source", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        result = inspect(args.host, args.port, args.secret_source)
    except Exception as exc:
        # Exception text can contain connection details; only its type is emitted.
        print("MySQL inspection failed (details redacted): " + type(exc).__name__)
        raise SystemExit(1)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Read-only MySQL metadata report saved; no data rows, secrets or SQL writes emitted")
