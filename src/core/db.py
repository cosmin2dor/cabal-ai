import os
from collections.abc import Generator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine


def _register_models() -> None:
    # Importing the models to be registered by the ORM
    import memory  # noqa: F401

    # Add here any additional models to be registered in the future


@lru_cache
def get_engine() -> Engine:
    db_url = os.environ.get("CABAL_DATABASE_URL", "sqlite:///./db/cabal.sqlite3")
    engine = create_engine(db_url)

    return engine


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = Session(get_engine(), expire_on_commit=False)

    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    _register_models()

    engine = get_engine()
    SQLModel.metadata.create_all(engine)


def reset_db() -> None:
    _register_models()

    engine = get_engine()
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
