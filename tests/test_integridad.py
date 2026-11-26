from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest


def solicitudes_simultaneas(enviar):
    inicio = Barrier(2)

    def ejecutar():
        inicio.wait(timeout=5)
        return enviar().status_code

    with ThreadPoolExecutor(max_workers=2) as grupo:
        futuros = [grupo.submit(ejecutar) for _ in range(2)]
        return sorted(futuro.result(timeout=15) for futuro in futuros)


def catalogo(client, stock):
    socio = client.post("/socios/", json={"nombre": "Ana", "email": "ana@example.com"})
    libro = client.post("/libros/", json={"titulo": "Biblioteca", "isbn": "A1",
                                          "stock": stock, "anio": 2025})
    assert socio.status_code == libro.status_code == 201
    return {"socio_id": socio.json()["id"], "libro_id": libro.json()["id"]}


@pytest.mark.parametrize("devuelto", [False, True])
def test_bajas_con_historial(client, devuelto):
    datos = catalogo(client, 1)
    prestamo = client.post("/prestamos/", json=datos).json()
    if devuelto:
        assert client.post(f"/prestamos/{prestamo['id']}/devolucion").status_code == 200
    for ruta in [f"/libros/{datos['libro_id']}", f"/socios/{datos['socio_id']}"]:
        assert client.delete(ruta).status_code == 409
        assert client.get(ruta).status_code == 200
    historial = client.get(f"/socios/{datos['socio_id']}/prestamos").json()
    assert [fila["id"] for fila in historial] == [prestamo["id"]]


@pytest.mark.parametrize("engine", ["archivo"], indirect=True)
@pytest.mark.parametrize("stock,previos", [(1, 0), (5, 2)])
def test_prestamos_simultaneos(client, engine, stock, previos):
    datos = catalogo(client, stock)
    for _ in range(previos):
        assert client.post("/prestamos/", json=datos).status_code == 201
    assert solicitudes_simultaneas(lambda: client.post("/prestamos/", json=datos)) == [201, 409]
    activos = client.get(f"/socios/{datos['socio_id']}/prestamos?activos=true").json()
    assert len(activos) == previos + 1
    assert client.get(f"/libros/{datos['libro_id']}").json()["stock"] == stock - previos - 1


@pytest.mark.parametrize("engine", ["archivo"], indirect=True)
def test_devolucion_simultanea(client, engine):
    datos = catalogo(client, 1)
    prestamo = client.post("/prestamos/", json=datos).json()
    url = f"/prestamos/{prestamo['id']}/devolucion"
    assert solicitudes_simultaneas(lambda: client.post(url)) == [200, 409]
    assert client.get(f"/libros/{datos['libro_id']}").json()["stock"] == 1


@pytest.mark.parametrize("engine", ["archivo"], indirect=True)
@pytest.mark.parametrize("ruta,datos", [
    ("/libros/", {"titulo": "Biblioteca", "isbn": "A1", "stock": 1, "anio": 2025}),
    ("/socios/", {"nombre": "Ana", "email": "ana@example.com"}),
])
def test_altas_duplicadas_simultaneas(client, engine, ruta, datos):
    assert solicitudes_simultaneas(lambda: client.post(ruta, json=datos)) == [201, 409]
    assert len(client.get(ruta).json()) == 1
