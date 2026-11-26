from fastapi import APIRouter, Depends

from dependencies import servicio_libros
from services.libros import ServicioLibros

from models.libro import LibroCrear, LibroActualizar, LibroPublico


router = APIRouter(prefix="/libros", tags=["Libros"])


@router.post("/", response_model=LibroPublico, status_code=201)
def crear_libro(datos: LibroCrear, servicio: ServicioLibros = Depends(servicio_libros)):
    return servicio.crear_libro(datos)


@router.get("/", response_model=list[LibroPublico])
def listar_libros(
    disponibles: bool = False,
    servicio: ServicioLibros = Depends(servicio_libros)
):
    return servicio.listar_libros(disponibles)


@router.get("/{id}", response_model=LibroPublico)
def obtener_libro(id: int, servicio: ServicioLibros = Depends(servicio_libros)):
    return servicio.obtener_libro(id)


@router.put("/{id}", response_model=LibroPublico)
def modificar_libro(
    id: int,
    datos: LibroActualizar,
    servicio: ServicioLibros = Depends(servicio_libros)
):
    return servicio.modificar_libro(id, datos)


@router.delete("/{id}")
def eliminar_libro(id: int, servicio: ServicioLibros = Depends(servicio_libros)):
    servicio.eliminar_libro(id)
    return {"mensaje": "Libro eliminado correctamente"}


@router.post("/{id}/autores/{autor_id}")
def asociar_autor(
    id: int,
    autor_id: int,
    servicio: ServicioLibros = Depends(servicio_libros)
):
    servicio.asociar_autor(id, autor_id)
    return {"mensaje": "Autor asociado correctamente"}
