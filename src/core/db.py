import os
from sqlmodel import SQLModel, create_engine


def get_engine():
    db_url = os.environ.get("CABAL_DATABASE_URL", "sqlite:///./db/cabal.sqlite3")
    engine = create_engine(db_url)

    return engine


def init_db():
    # Importing the models to be registered by the ORM
    import memory  # noqa: F401

    engine = get_engine()
    SQLModel.metadata.create_all(engine)
