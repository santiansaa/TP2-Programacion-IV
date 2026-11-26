from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

from dependencies import servicio_prestamos
from models.libro import Libro
from models.prestamo import Prestamo, PrestamoCrear
from models.socio import Socio
from repositories.libros import RepositorioLibros
from repositories.prestamos import RepositorioPrestamos
from repositories.socios import RepositorioSocios
from services.errores import Conflicto
from services.prestamos import ServicioPrestamos


@pytest.fixture
def datos(session):
    socio = Socio(nombre="Ana", email="ana@example.com")
    libro = Libro(titulo="Biblioteca", isbn="A1", stock=1, anio=2025)
    session.add_all([socio, libro])
    session.commit()
    return PrestamoCrear(socio_id=socio.id, libro_id=libro.id)


def test_servicio_delega_creacion_y_consulta(session, datos):
    servicio = servicio_prestamos(session)
    with patch.object(servicio.prestamos, "guardar", wraps=servicio.prestamos.guardar) as guardar:
        prestamo = servicio.crear_prestamo(datos)
        guardar.assert_called_once_with(prestamo)
    assert servicio.obtener_prestamos_socio(datos.socio_id, True) == [prestamo]


def test_servicio_calcula_multa_antes_de_guardar():
    hoy = date(2026, 11, 23)
    prestamo = Prestamo(id=7, socio_id=1, libro_id=2, fecha_prestamo=hoy - timedelta(days=17),
                        fecha_vencimiento=hoy - timedelta(days=3))
    libro = Libro(id=2, titulo="Biblioteca", isbn="A1", stock=0, anio=2025)
    prestamos = MagicMock(spec=RepositorioPrestamos)
    libros = MagicMock(spec=RepositorioLibros)
    servicio = ServicioPrestamos(prestamos, libros, MagicMock(spec=RepositorioSocios))
    prestamos.buscar.return_value = prestamo
    prestamos.guardar.side_effect = lambda entidad: entidad
    libros.buscar.return_value = libro
    with patch("services.prestamos.date") as fecha:
        fecha.today.return_value = hoy
        resultado = servicio.devolver_prestamo(7)
    assert resultado.fecha_devolucion == hoy
    assert resultado.multa == 300
    assert libro.stock == 1
    prestamos.guardar.assert_called_once_with(prestamo)
    libros.guardar.assert_called_once_with(libro)


def test_prestamo_y_stock_persisten_juntos(session, datos):
    servicio = servicio_prestamos(session)
    prestamo_id = servicio.crear_prestamo(datos).id
    with pytest.raises(Conflicto):
        servicio.crear_prestamo(datos)
    session.expunge_all()
    assert servicio.libros.buscar(datos.libro_id).stock == 0
    assert servicio.prestamos.buscar(prestamo_id).fecha_devolucion is None
    servicio.devolver_prestamo(prestamo_id)
    with pytest.raises(Conflicto):
        servicio.devolver_prestamo(prestamo_id)
    session.expunge_all()
    assert servicio.libros.buscar(datos.libro_id).stock == 1
    assert servicio.prestamos.buscar(prestamo_id).fecha_devolucion == date.today()
    assert servicio.obtener_prestamos_socio(datos.socio_id, True) == []


def test_fallo_al_guardar_prestamo_revierte_stock(session, datos):
    servicio = servicio_prestamos(session)
    with patch.object(servicio.prestamos, "guardar", side_effect=RuntimeError("fallo de escritura")):
        with pytest.raises(RuntimeError, match="fallo de escritura"):
            servicio.crear_prestamo(datos)
    session.expunge_all()
    assert servicio.libros.buscar(datos.libro_id).stock == 1
    assert servicio.obtener_prestamos_socio(datos.socio_id, False) == []
