
from sqlmodel import SQLModel, Field


class SocioBase(SQLModel):
    nombre: str
    email: str
    activo: bool = True


class Socio(SocioBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)


class SocioCrear(SocioBase):
    pass


class SocioActualizar(SocioBase):
    pass


class SocioPublico(SocioBase):
    id: int
