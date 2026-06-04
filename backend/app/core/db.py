from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def _engine_args(url: str) -> dict:
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {"pool_pre_ping": True}


settings = get_settings()
engine = create_engine(settings.database_url, **_engine_args(settings.database_url))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.models.entities import AuditLog, EvaluationResult, EvaluationRun, RegressionSnapshot, Report, User

    Base.metadata.create_all(bind=engine)
    sync_postgres_enums()


def sync_postgres_enums() -> None:
    if not settings.database_url.startswith("postgres"):
        return
    enum_values = ("privacy_leakage", "misinformation", "adversarial", "csam_avoidance")
    with engine.begin() as connection:
        for value in enum_values:
            connection.execute(text(f"ALTER TYPE attackcategory ADD VALUE IF NOT EXISTS '{value}'"))
