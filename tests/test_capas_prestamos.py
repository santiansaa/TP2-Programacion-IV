from datetime import date, timedelta
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from models.libro import Libro
from models.prestamo import Prestamo, PrestamoCrear
from models.socio import Socio
from repositories import prestamos as repo
from services import prestamos as servicio


@pytest.fixture
def datos(session):
    socio = Socio(nombre="Ana", email="ana@example.com")
    libro = Libro(titulo="Biblioteca", isbn="A1", stock=1, anio=2025)
    session.add_all([socio, libro])
    session.commit()
    return PrestamoCrear(socio_id=socio.id, libro_id=libro.id)


def test_servicio_delega_creacion_y_consulta(session, datos):
    with patch.object(servicio, "repo", wraps=repo) as llamadas:
        prestamo = servicio.crear_prestamo(datos, session)
        llamadas.buscar_socio.assert_called_once_with(session, datos.socio_id)
        llamadas.buscar_libro.assert_called_once_with(session, datos.libro_id)
        llamadas.listar_por_socio.assert_called_once_with(session, datos.socio_id, activos=True)
        libro = repo.buscar_libro(session, datos.libro_id)
        llamadas.guardar_con_libro.assert_called_once_with(session, prestamo, libro)

        llamadas.reset_mock()
        assert servicio.obtener_prestamos_socio(datos.socio_id, True, session) == [prestamo]
        llamadas.listar_por_socio.assert_called_once_with(session, datos.socio_id, True)


def test_servicio_calcula_multa_antes_de_guardar(datos):
    hoy = date(2026, 11, 23)
    prestamo = Prestamo(id=7, **datos.model_dump(), fecha_prestamo=hoy - timedelta(days=17),
                        fecha_vencimiento=hoy - timedelta(days=3))
    libro = Libro(id=datos.libro_id, titulo="Biblioteca", isbn="A1", stock=0, anio=2025)
    sesion = Mock(spec_set=[])
    with patch.object(servicio, "repo", autospec=True) as llamadas, patch.object(servicio, "date") as fecha:
        fecha.today.return_value = hoy
        llamadas.buscar_prestamo.return_value = prestamo
        llamadas.buscar_libro.return_value = libro
        resultado = servicio.devolver_prestamo(7, sesion)
        llamadas.buscar_prestamo.assert_called_once_with(sesion, 7)
        llamadas.buscar_libro.assert_called_once_with(sesion, datos.libro_id)
        llamadas.guardar_con_libro.assert_called_once_with(sesion, prestamo, libro)
    assert resultado.fecha_devolucion == hoy
    assert resultado.multa == 300
    assert libro.stock == 1


def test_prestamo_y_stock_persisten_juntos(session, datos):
    prestamo_id = servicio.crear_prestamo(datos, session).id
    with pytest.raises(HTTPException) as rechazo:
        servicio.crear_prestamo(datos, session)
    assert rechazo.value.status_code == 409
    session.rollback()
    session.expunge_all()
    assert repo.buscar_socio(session, datos.socio_id).email == "ana@example.com"
    assert repo.buscar_libro(session, datos.libro_id).stock == 0
    prestamo = repo.buscar_prestamo(session, prestamo_id)
    assert prestamo.fecha_devolucion is None
    assert repo.listar_por_socio(session, datos.socio_id, False) == [prestamo]

    servicio.devolver_prestamo(prestamo_id, session)
    with pytest.raises(HTTPException) as rechazo:
        servicio.devolver_prestamo(prestamo_id, session)
    assert rechazo.value.status_code == 409
    session.rollback()
    session.expunge_all()
    assert repo.buscar_libro(session, datos.libro_id).stock == 1
    assert repo.buscar_prestamo(session, prestamo_id).fecha_devolucion == date.today()
    assert repo.listar_por_socio(session, datos.socio_id, True) == []
