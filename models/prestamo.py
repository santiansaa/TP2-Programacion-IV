
from datetime import date
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .socio import Socio
    from .libro import Libro


class PrestamoBase(SQLModel):
    socio_id: int
    libro_id: int


class Prestamo(PrestamoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    socio_id: int = Field(foreign_key="socio.id")
    libro_id: int = Field(foreign_key="libro.id")

    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: date | None = None
    multa: int = 0

    socio: "Socio" = Relationship()
    libro: "Libro" = Relationship()


class PrestamoCrear(PrestamoBase):
    pass


class PrestamoPublico(PrestamoBase):
    id: int
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: date | None
    multa: int
