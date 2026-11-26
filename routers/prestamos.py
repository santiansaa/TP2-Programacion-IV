from fastapi import APIRouter, Depends

from dependencies import servicio_prestamos
from services.prestamos import ServicioPrestamos

from models.prestamo import PrestamoCrear, PrestamoPublico


router = APIRouter(prefix="/prestamos", tags=["Prestamos"])


@router.post("/", response_model=PrestamoPublico, status_code=201)
def registrar_prestamo(
    datos: PrestamoCrear,
    servicio: ServicioPrestamos = Depends(servicio_prestamos)
):
    return servicio.crear_prestamo(datos)


@router.post("/{id}/devolucion", response_model=PrestamoPublico)
def registrar_devolucion(
    id: int,
    servicio: ServicioPrestamos = Depends(servicio_prestamos)
):
    return servicio.devolver_prestamo(id)
