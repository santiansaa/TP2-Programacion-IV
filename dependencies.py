from fastapi import Depends
from sqlmodel import Session

from database import get_session
from repositories.autores import RepositorioAutores
from services.autores import ServicioAutores
from repositories.libros import RepositorioLibros
from services.libros import ServicioLibros
from repositories.socios import RepositorioSocios
from services.socios import ServicioSocios
from repositories.prestamos import RepositorioPrestamos
from services.prestamos import ServicioPrestamos


def servicio_autores(session: Session = Depends(get_session)) -> ServicioAutores:
    return ServicioAutores(RepositorioAutores(session))


def servicio_libros(session: Session = Depends(get_session)) -> ServicioLibros:
    return ServicioLibros(RepositorioLibros(session), RepositorioAutores(session))


def servicio_socios(session: Session = Depends(get_session)) -> ServicioSocios:
    return ServicioSocios(RepositorioSocios(session))


def servicio_prestamos(session: Session = Depends(get_session)) -> ServicioPrestamos:
    return ServicioPrestamos(RepositorioPrestamos(session), RepositorioLibros(session), RepositorioSocios(session))
