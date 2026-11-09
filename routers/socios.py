

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models.prestamo import PrestamoPublico
from services.prestamos import obtener_prestamos_socio
from database import get_session
from models.socio import Socio, SocioCrear, SocioActualizar, SocioPublico


router = APIRouter(prefix="/socios", tags=["Socios"])


@router.post("/", response_model=SocioPublico, status_code=201)
def crear_socio(datos: SocioCrear, session: Session = Depends(get_session)):
    existente = session.exec(
        select(Socio).where(Socio.email == datos.email)
    ).first()

    if existente:
        raise HTTPException(status_code=409, detail="Email duplicado")

    socio = Socio.model_validate(datos)
    session.add(socio)
    session.commit()
    session.refresh(socio)

    return socio


@router.get("/", response_model=list[SocioPublico])
def listar_socios(session: Session = Depends(get_session)):
    return session.exec(select(Socio)).all()


@router.get("/{id}", response_model=SocioPublico)
def obtener_socio(id: int, session: Session = Depends(get_session)):
    socio = session.get(Socio, id)

    if socio is None:
        raise HTTPException(status_code=404, detail="Socio no encontrado")

    return socio


@router.put("/{id}", response_model=SocioPublico)
def modificar_socio(
    id: int,
    datos: SocioActualizar,
    session: Session = Depends(get_session)
):
    socio = session.get(Socio, id)

    if socio is None:
        raise HTTPException(status_code=404, detail="Socio no encontrado")

    existente = session.exec(
        select(Socio).where(
            Socio.email == datos.email,
            Socio.id != id
        )
    ).first()

    if existente:
        raise HTTPException(status_code=409, detail="Email duplicado")

    socio.nombre = datos.nombre
    socio.email = datos.email
    socio.activo = datos.activo

    session.add(socio)
    session.commit()
    session.refresh(socio)

    return socio


@router.delete("/{id}")
def eliminar_socio(id: int, session: Session = Depends(get_session)):
    socio = session.get(Socio, id)

    if socio is None:
        raise HTTPException(status_code=404, detail="Socio no encontrado")

    session.delete(socio)
    session.commit()

    return {"mensaje": "Socio eliminado correctamente"}


@router.get("/{id}/prestamos", response_model=list[PrestamoPublico])
def listar_prestamos_socio(
    id: int,
    activos: bool = False,
    session: Session = Depends(get_session)
):
    return obtener_prestamos_socio(id, activos, session)
