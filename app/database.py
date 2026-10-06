from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"

# SQLite blocks cross-thread use by default; FastAPI may handle
# requests on different threads, so we turn that check off.

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency: opens a session for each request and always closes it,
# even if the route raises an error. Tests override this in conftest.py.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()