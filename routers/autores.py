
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models.autor import Autor, AutorCrear, AutorActualizar, AutorPublico


router = APIRouter(prefix="/autores", tags=["Autores"])


@router.post("/", response_model=AutorPublico, status_code=201)
def crear_autor(datos: AutorCrear, session: Session = Depends(get_session)):
    autor = Autor.model_validate(datos)

    session.add(autor)
    session.commit()
    session.refresh(autor)

    return autor


@router.get("/", response_model=list[AutorPublico])
def listar_autores(session: Session = Depends(get_session)):
    return session.exec(select(Autor)).all()


@router.get("/{id}", response_model=AutorPublico)
def obtener_autor(id: int, session: Session = Depends(get_session)):
    autor = session.get(Autor, id)

    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    return autor


@router.put("/{id}", response_model=AutorPublico)
def modificar_autor(
    id: int,
    datos: AutorActualizar,
    session: Session = Depends(get_session)
):
    autor = session.get(Autor, id)

    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    autor.nombre = datos.nombre
    autor.nacionalidad = datos.nacionalidad

    session.add(autor)
    session.commit()
    session.refresh(autor)

    return autor


@router.delete("/{id}")
def eliminar_autor(id: int, session: Session = Depends(get_session)):
    autor = session.get(Autor, id)

    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    session.delete(autor)
    session.commit()

    return {"mensaje": "Autor eliminado correctamente"}

