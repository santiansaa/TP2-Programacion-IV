
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models.autor import Autor

from database import get_session
from models.libro import Libro, LibroCrear, LibroActualizar, LibroPublico


router = APIRouter(prefix="/libros", tags=["Libros"])


@router.post("/", response_model=LibroPublico, status_code=201)
def crear_libro(datos: LibroCrear, session: Session = Depends(get_session)):
    existente = session.exec(
        select(Libro).where(Libro.isbn == datos.isbn)
    ).first()

    if existente:
        raise HTTPException(status_code=409, detail="ISBN duplicado")

    libro = Libro.model_validate(datos)

    session.add(libro)
    session.commit()
    session.refresh(libro)

    return libro


@router.get("/", response_model=list[LibroPublico])
def listar_libros(
    disponibles: bool = False,
    session: Session = Depends(get_session)
):
    consulta = select(Libro)

    if disponibles:
        consulta = consulta.where(Libro.stock > 0)

    return session.exec(consulta).all()


@router.get("/{id}", response_model=LibroPublico)
def obtener_libro(id: int, session: Session = Depends(get_session)):
    libro = session.get(Libro, id)

    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    return libro


@router.put("/{id}", response_model=LibroPublico)
def modificar_libro(
    id: int,
    datos: LibroActualizar,
    session: Session = Depends(get_session)
):
    libro = session.get(Libro, id)

    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    existente = session.exec(
        select(Libro).where(
            Libro.isbn == datos.isbn,
            Libro.id != id
        )
    ).first()

    if existente:
        raise HTTPException(status_code=409, detail="ISBN duplicado")

    libro.titulo = datos.titulo
    libro.isbn = datos.isbn
    libro.stock = datos.stock
    libro.anio = datos.anio

    session.add(libro)
    session.commit()
    session.refresh(libro)

    return libro


@router.delete("/{id}")
def eliminar_libro(id: int, session: Session = Depends(get_session)):
    libro = session.get(Libro, id)

    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    session.delete(libro)
    session.commit()

    return {"mensaje": "Libro eliminado correctamente"}
    

    
@router.post("/{id}/autores/{autor_id}")
def asociar_autor(
    id: int,
    autor_id: int,
    session: Session = Depends(get_session)
):
    libro = session.get(Libro, id)
    autor = session.get(Autor, autor_id)

    if libro is None or autor is None:
        raise HTTPException(
            status_code=404,
            detail="Libro o autor no encontrado"
        )

    if autor not in libro.autores:
        libro.autores.append(autor)
        session.add(libro)
        session.commit()

    return {"mensaje": "Autor asociado correctamente"}


