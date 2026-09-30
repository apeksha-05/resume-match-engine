from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class every SQLAlchemy model inherits from."""

    pass


def get_db():
    """FastAPI dependency: yields a database session and always closes it."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()