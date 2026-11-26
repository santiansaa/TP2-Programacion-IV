from contextlib import contextmanager
from sqlite3 import SQLITE_CONSTRAINT_FOREIGNKEY, SQLITE_CONSTRAINT_UNIQUE
from typing import Generic, TypeVar

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel

Entidad = TypeVar("Entidad", bound=SQLModel)


class ValorDuplicado(Exception):
    pass


class RegistroReferenciado(Exception):
    pass


class Repositorio(Generic[Entidad]):
    modelo: type[Entidad]

    def __init__(self, session: Session):
        self.session = session

    def buscar(self, id: int) -> Entidad | None:
        return self.session.get(self.modelo, id)

    @contextmanager
    def escritura(self):
        """Reservar la escritura en SQLite antes de leer los datos a modificar."""
        try:
            self.session.execute(text("BEGIN IMMEDIATE"))
            yield
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            codigo = getattr(error.orig, "sqlite_errorcode", None)
            if codigo == SQLITE_CONSTRAINT_UNIQUE:
                raise ValorDuplicado from error
            if codigo == SQLITE_CONSTRAINT_FOREIGNKEY:
                raise RegistroReferenciado from error
            raise
        except Exception:
            self.session.rollback()
            raise

    def guardar(self, entidad: Entidad) -> Entidad:
        self.session.add(entidad)
        self.session.flush()
        return entidad

    def eliminar(self, entidad: Entidad) -> None:
        self.session.delete(entidad)
