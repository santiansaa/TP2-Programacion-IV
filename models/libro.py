
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import CheckConstraint
from .libro_autor import LibroAutor
from .autor import AutorPublico

if TYPE_CHECKING:
    from .autor import Autor


class LibroBase(SQLModel):
    titulo: str
    isbn: str
    stock: int = Field(ge=0)
    anio: int


class Libro(LibroBase, table=True):
    __table_args__ = (
        CheckConstraint("stock >= 0", name="check_stock_positivo"),
    )

    id: int | None = Field(default=None, primary_key=True)

    isbn: str = Field(unique=True)

    autores: list["Autor"] = Relationship(
        back_populates="libros",
        link_model=LibroAutor
    )


class LibroCrear(LibroBase):
    pass


class LibroActualizar(LibroBase):
    pass


class LibroPublico(LibroBase):
    id: int
    autores: list[AutorPublico] = []