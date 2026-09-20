"""SQLite + SQLAlchemy 세션/엔진 설정."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DB_PATH, DATA_DIR, IMAGES_DIR


class Base(DeclarativeBase):
    pass


def _ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)


_ensure_dirs()

# check_same_thread=False: FastAPI 스레드풀에서 세션 사용 허용
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


def init_db() -> None:
    """테이블 생성. 모델 import 후 호출."""
    from . import models  # noqa: F401  (모델 등록)

    Base.metadata.create_all(bind=engine)


def get_session():
    """FastAPI 의존성: 요청마다 세션 제공."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
