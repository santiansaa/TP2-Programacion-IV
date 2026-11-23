from sqlmodel import Session, select

from models.libro import Libro
from models.prestamo import Prestamo
from models.socio import Socio


def buscar_socio(session: Session, socio_id: int):
    return session.get(Socio, socio_id)


def buscar_libro(session: Session, libro_id: int):
    return session.get(Libro, libro_id)


def buscar_prestamo(session: Session, prestamo_id: int):
    return session.get(Prestamo, prestamo_id)


def listar_por_socio(session: Session, socio_id: int, activos: bool):
    consulta = select(Prestamo).where(
        Prestamo.socio_id == socio_id
    )

    if activos:
        consulta = consulta.where(
            Prestamo.fecha_devolucion == None
        )

    return session.exec(consulta).all()


def guardar_con_libro(session: Session, prestamo: Prestamo, libro: Libro):
    session.add(prestamo)
    session.add(libro)
    session.commit()
    session.refresh(prestamo)
