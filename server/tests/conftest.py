"""테스트 공용 픽스처. 각 테스트마다 깨끗한 DB."""
import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine, init_db
from app.main import app


@pytest.fixture()
def client():
    # 깨끗한 스키마
    Base.metadata.drop_all(bind=engine)
    init_db()
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    init_db()


@pytest.fixture()
def db_session():
    from app.db import SessionLocal
    Base.metadata.drop_all(bind=engine)
    init_db()
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()
