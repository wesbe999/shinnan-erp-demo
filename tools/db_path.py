from pathlib import Path

from app.db import DATABASE_URL


def current_sqlite_path() -> Path:
    if not DATABASE_URL.startswith("sqlite:///"):
        raise RuntimeError(f"Expected sqlite DATABASE_URL, got: {DATABASE_URL}")

    raw_path = DATABASE_URL.removeprefix("sqlite:///")
    return Path(raw_path)
