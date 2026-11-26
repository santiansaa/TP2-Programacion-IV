from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlmodel import create_engine

import database
from main import app


def test_arranque_y_persistencia_entre_sesiones(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'biblioteca.db'}")
    event.listen(engine, "connect", database.activar_foreign_keys)
    monkeypatch.setattr(database, "engine", engine)
    try:
        with TestClient(app) as client:
            assert client.get("/").status_code == 200
            alta = client.post("/autores/", json={"nombre": "Borges", "nacionalidad": "Argentina"})
            assert alta.status_code == 201
            autor = alta.json()
        with TestClient(app) as client:
            consulta = client.get(f"/autores/{autor['id']}")
            assert consulta.status_code == 200
            assert consulta.json() == autor
    finally:
        engine.dispose()
