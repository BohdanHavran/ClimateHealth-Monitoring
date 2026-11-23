import os


def get_db_password():
    """Read a bounded Docker secret file, or DB_PASS for local development."""
    secret_path = os.getenv("DB_PASS_FILE")
    if secret_path:
        try:
            with open(secret_path, "rb") as secret_file:
                value = secret_file.read(4097)
            if len(value) > 4096:
                raise ValueError("Database password file is too large")
            password = value.decode("utf-8").strip()
        except (OSError, UnicodeError) as exc:
            raise ValueError("Database password file cannot be read") from exc
    else:
        password = os.getenv("DB_PASS", "")
    if not password or "\x00" in password:
        raise ValueError("Database password is not configured")
    return password
