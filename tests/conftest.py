import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

import database
from main import app


@pytest.fixture
def engine(request, tmp_path, monkeypatch):
    if getattr(request, "param", None) == "archivo":
        motor = create_engine(f"sqlite:///{tmp_path / 'biblioteca.db'}")
    else:
        motor = create_engine("sqlite://", connect_args={"check_same_thread": False},
                              poolclass=StaticPool)
    event.listen(motor, "connect", database.activar_foreign_keys)
    monkeypatch.setattr(database, "engine", motor)
    database.crear_db()
    yield motor
    motor.dispose()


@pytest.fixture
def session(engine):
    with Session(engine, expire_on_commit=False) as sesion:
        yield sesion


@pytest.fixture
def client(engine):
    with TestClient(app) as cliente:
        yield cliente
