from sqlmodel import select

from models.socio import Socio
from repositories.persistencia import Repositorio


class RepositorioSocios(Repositorio[Socio]):
    modelo = Socio

    def listar(self) -> list[Socio]:
        consulta = select(Socio)
        return list(self.session.exec(consulta).all())
