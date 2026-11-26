from sqlmodel import select
from sqlalchemy.orm import selectinload
from models.autor import Autor

from models.libro import Libro
from repositories.persistencia import Repositorio


class RepositorioLibros(Repositorio[Libro]):
    modelo = Libro

    def listar(self, disponibles: bool) -> list[Libro]:
        consulta = select(Libro).options(selectinload(Libro.autores))
        if disponibles:
            consulta = consulta.where(Libro.stock > 0)
        return list(self.session.exec(consulta).all())

    def buscar(self, id: int) -> Libro | None:
        consulta = select(Libro).where(Libro.id == id).options(selectinload(Libro.autores))
        return self.session.exec(consulta).first()

    def asociar(self, libro: Libro, autor: Autor) -> None:
        if autor not in libro.autores:
            libro.autores.append(autor)
