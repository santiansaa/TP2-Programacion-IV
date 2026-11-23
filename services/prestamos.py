

from datetime import date, timedelta

from fastapi import HTTPException
from sqlmodel import Session

from models.prestamo import Prestamo, PrestamoCrear
from repositories import prestamos as repo


def crear_prestamo(datos: PrestamoCrear, session: Session):
    socio = repo.buscar_socio(session, datos.socio_id)
    libro = repo.buscar_libro(session, datos.libro_id)

    if socio is None or libro is None:
        raise HTTPException(
            status_code=404,
            detail="Socio o libro no encontrado"
        )

    if not socio.activo:
        raise HTTPException(
            status_code=403,
            detail="El socio esta inactivo"
        )

    prestamos_activos = repo.listar_por_socio(session, datos.socio_id, activos=True)

    if len(prestamos_activos) >= 3:
        raise HTTPException(
            status_code=409,
            detail="El socio ya tiene 3 prestamos activos"
        )

    if libro.stock <= 0:
        raise HTTPException(
            status_code=409,
            detail="No hay stock disponible"
        )

    hoy = date.today()

    prestamo = Prestamo(
        socio_id=datos.socio_id,
        libro_id=datos.libro_id,
        fecha_prestamo=hoy,
        fecha_vencimiento=hoy + timedelta(days=14)
    )

    libro.stock -= 1

    repo.guardar_con_libro(session, prestamo, libro)

    return prestamo


def devolver_prestamo(id: int, session: Session):
    prestamo = repo.buscar_prestamo(session, id)

    if prestamo is None:
        raise HTTPException(
            status_code=404,
            detail="Prestamo no encontrado"
        )

    if prestamo.fecha_devolucion is not None:
        raise HTTPException(
            status_code=409,
            detail="El prestamo ya fue devuelto"
        )

    hoy = date.today()

    dias_atraso = max(
        (hoy - prestamo.fecha_vencimiento).days,
        0
    )

    prestamo.fecha_devolucion = hoy
    prestamo.multa = dias_atraso * 100

    libro = repo.buscar_libro(session, prestamo.libro_id)
    libro.stock += 1

    repo.guardar_con_libro(session, prestamo, libro)

    return prestamo


def obtener_prestamos_socio(
    id: int,
    activos: bool,
    session: Session
):
    socio = repo.buscar_socio(session, id)

    if socio is None:
        raise HTTPException(
            status_code=404,
            detail="Socio no encontrado"
        )

    return repo.listar_por_socio(session, id, activos)
