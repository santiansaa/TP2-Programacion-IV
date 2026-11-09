

from datetime import date, timedelta

from models.prestamo import Prestamo


# DATOS DE PRUEBA

def crear_socio(client, activo=True, email="socio@test.com"):
    return client.post("/socios/", json={
        "nombre": "Socio Prueba",
        "email": email,
        "activo": activo
    }).json()


def crear_libro(client, stock=5, isbn="ISBN-001"):
    return client.post("/libros/", json={
        "titulo": "Libro Prueba",
        "isbn": isbn,
        "stock": stock,
        "anio": 2025
    }).json()


# AUTORES

def test_crud_autores(client):
    respuesta = client.post("/autores/", json={
        "nombre": "Borges",
        "nacionalidad": "Argentina"
    })
    assert respuesta.status_code == 201
    autor_id = respuesta.json()["id"]

    assert client.get("/autores/").status_code == 200
    assert client.get(f"/autores/{autor_id}").status_code == 200

    respuesta = client.put(f"/autores/{autor_id}", json={
        "nombre": "Jorge Luis Borges",
        "nacionalidad": "Argentina"
    })
    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Jorge Luis Borges"

    assert client.delete(f"/autores/{autor_id}").status_code == 200


def test_autor_inexistente(client):
    assert client.get("/autores/999").status_code == 404
    assert client.put("/autores/999", json={
        "nombre": "Test",
        "nacionalidad": "Argentina"
    }).status_code == 404
    assert client.delete("/autores/999").status_code == 404


# LIBROS

def test_crud_libros(client):
    libro = crear_libro(client)
    libro_id = libro["id"]

    assert client.get("/libros/").status_code == 200
    assert client.get(f"/libros/{libro_id}").status_code == 200

    respuesta = client.put(f"/libros/{libro_id}", json={
        "titulo": "Libro Actualizado",
        "isbn": "ISBN-001",
        "stock": 3,
        "anio": 2026
    })

    assert respuesta.status_code == 200
    assert respuesta.json()["stock"] == 3
    assert client.delete(f"/libros/{libro_id}").status_code == 200


def test_libro_inexistente(client):
    assert client.get("/libros/999").status_code == 404
    assert client.put("/libros/999", json={
        "titulo": "Test",
        "isbn": "OTRO",
        "stock": 1,
        "anio": 2025
    }).status_code == 404
    assert client.delete("/libros/999").status_code == 404


def test_isbn_duplicado(client):
    crear_libro(client)

    respuesta = client.post("/libros/", json={
        "titulo": "Otro libro",
        "isbn": "ISBN-001",
        "stock": 2,
        "anio": 2025
    })

    assert respuesta.status_code == 409

    otro = crear_libro(client, isbn="ISBN-002")
    respuesta = client.put(f"/libros/{otro['id']}", json={
        "titulo": "Otro libro",
        "isbn": "ISBN-001",
        "stock": 2,
        "anio": 2025
    })
    assert respuesta.status_code == 409


def test_stock_y_disponibilidad(client):
    crear_libro(client, stock=0, isbn="SIN-STOCK")
    crear_libro(client, stock=3, isbn="CON-STOCK")

    respuesta = client.get("/libros/?disponibles=true")

    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1

    respuesta = client.post("/libros/", json={
        "titulo": "Stock negativo",
        "isbn": "NEGATIVO",
        "stock": -1,
        "anio": 2025
    })
    assert respuesta.status_code == 422


def test_asociar_autor(client):
    libro = crear_libro(client)

    autor = client.post("/autores/", json={
        "nombre": "Borges",
        "nacionalidad": "Argentina"
    }).json()

    url = f"/libros/{libro['id']}/autores/{autor['id']}"

    assert client.post(url).status_code == 200
    assert client.post(url).status_code == 200

    respuesta = client.get(f"/libros/{libro['id']}")
    assert len(respuesta.json()["autores"]) == 1

    assert client.post("/libros/999/autores/999").status_code == 404


# SOCIOS

def test_crud_socios(client):
    socio = crear_socio(client)
    socio_id = socio["id"]

    assert client.get("/socios/").status_code == 200
    assert client.get(f"/socios/{socio_id}").status_code == 200

    respuesta = client.put(f"/socios/{socio_id}", json={
        "nombre": "Socio Actualizado",
        "email": "nuevo@test.com",
        "activo": False
    })

    assert respuesta.status_code == 200
    assert respuesta.json()["activo"] is False
    assert client.delete(f"/socios/{socio_id}").status_code == 200


def test_socio_inexistente(client):
    assert client.get("/socios/999").status_code == 404
    assert client.put("/socios/999", json={
        "nombre": "Test",
        "email": "test@test.com",
        "activo": True
    }).status_code == 404
    assert client.delete("/socios/999").status_code == 404


def test_email_duplicado(client):
    crear_socio(client)

    respuesta = client.post("/socios/", json={
        "nombre": "Otro",
        "email": "socio@test.com",
        "activo": True
    })

    assert respuesta.status_code == 409

    otro = crear_socio(client, email="otro@test.com")
    respuesta = client.put(f"/socios/{otro['id']}", json={
        "nombre": "Otro",
        "email": "socio@test.com",
        "activo": True
    })
    assert respuesta.status_code == 409


# PRESTAMOS

def test_crear_prestamo(client):
    socio = crear_socio(client)
    libro = crear_libro(client)

    respuesta = client.post("/prestamos/", json={
        "socio_id": socio["id"],
        "libro_id": libro["id"]
    })

    assert respuesta.status_code == 201

    prestamo = respuesta.json()

    inicio = date.fromisoformat(prestamo["fecha_prestamo"])
    vencimiento = date.fromisoformat(prestamo["fecha_vencimiento"])

    assert (vencimiento - inicio).days == 14
    assert prestamo["fecha_devolucion"] is None

    libro_actual = client.get(f"/libros/{libro['id']}").json()
    assert libro_actual["stock"] == 4


def test_socio_inactivo(client):
    socio = crear_socio(client, activo=False)
    libro = crear_libro(client)

    respuesta = client.post("/prestamos/", json={
        "socio_id": socio["id"],
        "libro_id": libro["id"]
    })

    assert respuesta.status_code == 403


def test_maximo_tres_prestamos(client):
    socio = crear_socio(client)
    libro = crear_libro(client)

    datos = {
        "socio_id": socio["id"],
        "libro_id": libro["id"]
    }

    for _ in range(3):
        assert client.post("/prestamos/", json=datos).status_code == 201

    assert client.post("/prestamos/", json=datos).status_code == 409


def test_prestamo_sin_stock(client):
    socio = crear_socio(client)
    libro = crear_libro(client, stock=0)

    respuesta = client.post("/prestamos/", json={
        "socio_id": socio["id"],
        "libro_id": libro["id"]
    })

    assert respuesta.status_code == 409


def test_prestamo_recurso_inexistente(client):
    assert client.post("/prestamos/", json={
        "socio_id": 999,
        "libro_id": 999
    }).status_code == 404

    socio = crear_socio(client)
    assert client.post("/prestamos/", json={
        "socio_id": socio["id"],
        "libro_id": 999
    }).status_code == 404


# DEVOLUCIONES

def test_devolucion_correcta(client):
    socio = crear_socio(client)
    libro = crear_libro(client)

    prestamo = client.post("/prestamos/", json={
        "socio_id": socio["id"],
        "libro_id": libro["id"]
    }).json()

    respuesta = client.post(
        f"/prestamos/{prestamo['id']}/devolucion"
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["multa"] == 0
    assert respuesta.json()["fecha_devolucion"] is not None

    libro_actual = client.get(f"/libros/{libro['id']}").json()
    assert libro_actual["stock"] == 5

    respuesta = client.post(
        f"/prestamos/{prestamo['id']}/devolucion"
    )
    assert respuesta.status_code == 409


def test_devolucion_inexistente(client):
    assert client.post(
        "/prestamos/999/devolucion"
    ).status_code == 404


def test_multa_por_atraso(client, session):
    socio = crear_socio(client)
    libro = crear_libro(client)

    prestamo = client.post("/prestamos/", json={
        "socio_id": socio["id"],
        "libro_id": libro["id"]
    }).json()

    # Simulamos una devolución con 3 días de atraso.
    registro = session.get(Prestamo, prestamo["id"])
    registro.fecha_vencimiento = date.today() - timedelta(days=3)
    session.add(registro)
    session.commit()

    respuesta = client.post(
        f"/prestamos/{prestamo['id']}/devolucion"
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["multa"] == 300


# CONSULTAS DE PRESTAMOS POR SOCIO

def test_consultar_prestamos_socio(client):
    socio = crear_socio(client)
    libro = crear_libro(client)

    prestamo = client.post("/prestamos/", json={
        "socio_id": socio["id"],
        "libro_id": libro["id"]
    }).json()

    url = f"/socios/{socio['id']}/prestamos"

    assert len(client.get(url).json()) == 1
    assert len(client.get(url + "?activos=true").json()) == 1

    client.post(f"/prestamos/{prestamo['id']}/devolucion")

    assert len(client.get(url).json()) == 1
    assert len(client.get(url + "?activos=true").json()) == 0

    assert client.get(
        "/socios/999/prestamos?activos=true"
    ).status_code == 404
