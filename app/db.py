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

            # 只要 buildings 有資料就算有資料
            buildings_exists = conn.execute(text("""
                SELECT COUNT(*) FROM sqlite_master
                WHERE type='table' AND name='buildings'
            """)).scalar_one()
            if int(buildings_exists or 0) > 0:
                building_count = conn.execute(text("SELECT COUNT(*) FROM buildings")).scalar_one()
                if int(building_count or 0) > 0:
                    return True

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
    # DB 已直接存放在 repo，不需要 seed
    return


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
