import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _path_from_env(env_name: str, default: str) -> Path:
    raw = os.getenv(env_name, default).strip() or default
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


DATA_DIR = _path_from_env("XUNNAN_DATA_DIR", "data")


def data_file(name: str) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / name


def database_url() -> str:
    explicit_url = os.getenv("DATABASE_URL", "").strip()
    if explicit_url:
        return explicit_url

    db_path = _path_from_env("XUNNAN_DB_PATH", "xunnan_dispatch.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return "sqlite:///" + db_path.as_posix()
