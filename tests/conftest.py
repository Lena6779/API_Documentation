import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_TEST_URL = "sqlite://"

# In-memory database: created fresh for tests, never touches tasks.db.
# StaticPool makes every session share one connection; without it,
# each connection would get its own empty in-memory database.
engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def client():
    """Provide a TestClient backed by a fresh in-memory database."""
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Make every route that depends on get_db use the test database instead
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client
     # Teardown: runs after each test so the next one starts clean
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)