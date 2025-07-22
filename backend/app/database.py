from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
from .db.models import Base

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        if settings.env == "azure" and settings.cosmos_endpoint:
            uri = settings.cosmos_endpoint
        else:
            uri = f"sqlite:///{settings.sqlite_db}"
        _engine = create_engine(uri, connect_args={"check_same_thread": False})
    return _engine


def get_session():
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal()


def init_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
