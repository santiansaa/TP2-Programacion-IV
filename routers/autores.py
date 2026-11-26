from fastapi import APIRouter, Depends

from dependencies import servicio_autores
from services.autores import ServicioAutores

from models.autor import AutorCrear, AutorActualizar, AutorPublico


router = APIRouter(prefix="/autores", tags=["Autores"])


@router.post("/", response_model=AutorPublico, status_code=201)
def crear_autor(datos: AutorCrear, servicio: ServicioAutores = Depends(servicio_autores)):
    return servicio.crear_autor(datos)


@router.get("/", response_model=list[AutorPublico])
def listar_autores(servicio: ServicioAutores = Depends(servicio_autores)):
    return servicio.listar_autores()


@router.get("/{id}", response_model=AutorPublico)
def obtener_autor(id: int, servicio: ServicioAutores = Depends(servicio_autores)):
    return servicio.obtener_autor(id)


@router.put("/{id}", response_model=AutorPublico)
def modificar_autor(
    id: int,
    datos: AutorActualizar,
    servicio: ServicioAutores = Depends(servicio_autores)
):
    return servicio.modificar_autor(id, datos)


@router.delete("/{id}")
def eliminar_autor(id: int, servicio: ServicioAutores = Depends(servicio_autores)):
    servicio.eliminar_autor(id)
    return {"mensaje": "Autor eliminado correctamente"}
