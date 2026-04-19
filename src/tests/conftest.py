import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["CABAL_DATABASE_URL"] = f"sqlite:///{_THIS_DIR}/test.sqlite3"

import pytest
from core.db import get_session, reset_db
from sqlmodel import Session
from typing import Generator


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    reset_db()
    yield


@pytest.fixture()
def session() -> Generator[Session, None, None]:
    with get_session() as session:
        yield session
