

from datetime import date, timedelta

from fastapi import HTTPException
from sqlmodel import Session, select

from models.socio import Socio
from models.libro import Libro
from models.prestamo import Prestamo, PrestamoCrear


def crear_prestamo(datos: PrestamoCrear, session: Session):
    socio = session.get(Socio, datos.socio_id)
    libro = session.get(Libro, datos.libro_id)

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

    prestamos_activos = session.exec(
        select(Prestamo).where(
            Prestamo.socio_id == datos.socio_id,
            Prestamo.fecha_devolucion == None
        )
    ).all()

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

    session.add(prestamo)
    session.add(libro)
    session.commit()
    session.refresh(prestamo)

    return prestamo


def devolver_prestamo(id: int, session: Session):
    prestamo = session.get(Prestamo, id)

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

    libro = session.get(Libro, prestamo.libro_id)
    libro.stock += 1

    session.add(prestamo)
    session.add(libro)
    session.commit()
    session.refresh(prestamo)

    return prestamo


def obtener_prestamos_socio(
    id: int,
    activos: bool,
    session: Session
):
    socio = session.get(Socio, id)

    if socio is None:
        raise HTTPException(
            status_code=404,
            detail="Socio no encontrado"
        )

    consulta = select(Prestamo).where(
        Prestamo.socio_id == id
    )

    if activos:
        consulta = consulta.where(
            Prestamo.fecha_devolucion == None
        )

    return session.exec(consulta).all()
