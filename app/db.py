from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import text
import os

from app.config import PROJECT_ROOT, database_url

DATABASE_URL = database_url()

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def _demo_seed_enabled() -> bool:
    value = os.getenv("XUNNAN_AUTO_SEED_DEMO", "1").strip().lower()
    return value not in {"0", "false", "no", "off"}


def _has_existing_data() -> bool:
    try:
        with engine.begin() as conn:
            table_count = conn.execute(text("""
                SELECT COUNT(*)
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
            """)).scalar_one()
            if int(table_count or 0) == 0:
                return False

            tickets_exists = conn.execute(text("""
                SELECT COUNT(*)
                FROM sqlite_master
                WHERE type = 'table'
                  AND name = 'tickets'
            """)).scalar_one()
            if int(tickets_exists or 0) == 0:
                return True

            ticket_count = conn.execute(text("SELECT COUNT(*) FROM tickets")).scalar_one()
            return int(ticket_count or 0) > 0
    except Exception:
        return True


def seed_demo_database_if_needed() -> None:
    if not _demo_seed_enabled():
        return

    if not DATABASE_URL.startswith("sqlite"):
        return

    if _has_existing_data():
        return

    seed_path = PROJECT_ROOT / "app" / "seed" / "demo_seed.sql"
    if not seed_path.exists():
        return

    raw_conn = engine.raw_connection()
    try:
        raw_conn.executescript(seed_path.read_text(encoding="utf-8"))
        raw_conn.execute("DELETE FROM employee_sessions")
        raw_conn.execute("DROP TABLE IF EXISTS _codex_write_probe")
        raw_conn.commit()
    finally:
        raw_conn.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
