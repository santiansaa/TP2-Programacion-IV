

from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from models.prestamo import PrestamoCrear, PrestamoPublico
from services.prestamos import crear_prestamo, devolver_prestamo


router = APIRouter(prefix="/prestamos", tags=["Prestamos"])


@router.post("/", response_model=PrestamoPublico, status_code=201)
def registrar_prestamo(
    datos: PrestamoCrear,
    session: Session = Depends(get_session)
):
    return crear_prestamo(datos, session)


@router.post("/{id}/devolucion", response_model=PrestamoPublico)
def registrar_devolucion(
    id: int,
    session: Session = Depends(get_session)
):
    return devolver_prestamo(id, session)
