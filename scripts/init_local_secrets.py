"""Create local random passwords without displaying or replacing existing values."""
from pathlib import Path
import os
import secrets

root = Path(__file__).resolve().parents[1]
folder = root / ".secrets"
folder.mkdir(exist_ok=True, mode=0o700)
for name in ("mysql_password", "mysql_root_password"):
    path = folder / name
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        print(f"Kept existing secret file: {name}")
        continue
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(secrets.token_urlsafe(32))
    print(f"Created secret file: {name}")
print("Secrets are not encrypted by Compose. Protect directory permissions and do not commit it.")
