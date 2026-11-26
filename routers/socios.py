from fastapi import APIRouter, Depends

from dependencies import servicio_socios, servicio_prestamos
from services.socios import ServicioSocios
from services.prestamos import ServicioPrestamos
from models.prestamo import PrestamoPublico
from models.socio import SocioCrear, SocioActualizar, SocioPublico


router = APIRouter(prefix="/socios", tags=["Socios"])


@router.post("/", response_model=SocioPublico, status_code=201)
def crear_socio(datos: SocioCrear, servicio: ServicioSocios = Depends(servicio_socios)):
    return servicio.crear_socio(datos)


@router.get("/", response_model=list[SocioPublico])
def listar_socios(servicio: ServicioSocios = Depends(servicio_socios)):
    return servicio.listar_socios()


@router.get("/{id}", response_model=SocioPublico)
def obtener_socio(id: int, servicio: ServicioSocios = Depends(servicio_socios)):
    return servicio.obtener_socio(id)


@router.put("/{id}", response_model=SocioPublico)
def modificar_socio(
    id: int,
    datos: SocioActualizar,
    servicio: ServicioSocios = Depends(servicio_socios)
):
    return servicio.modificar_socio(id, datos)


@router.delete("/{id}")
def eliminar_socio(id: int, servicio: ServicioSocios = Depends(servicio_socios)):
    servicio.eliminar_socio(id)
    return {"mensaje": "Socio eliminado correctamente"}


@router.get("/{id}/prestamos", response_model=list[PrestamoPublico])
def listar_prestamos_socio(
    id: int,
    activos: bool = False,
    servicio: ServicioPrestamos = Depends(servicio_prestamos)
):
    return servicio.obtener_prestamos_socio(id, activos)
