
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from .libro_autor import LibroAutor

if TYPE_CHECKING:
    from .libro import Libro


class AutorBase(SQLModel):
    nombre: str
    nacionalidad: str


class Autor(AutorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    libros: list["Libro"] = Relationship(
        back_populates="autores",
        link_model=LibroAutor
    )


class AutorCrear(AutorBase):
    pass


class AutorActualizar(AutorBase):
    pass


class AutorPublico(AutorBase):
    id: int
