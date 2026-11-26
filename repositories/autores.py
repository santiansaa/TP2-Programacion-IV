from sqlmodel import select

from models.autor import Autor
from repositories.persistencia import Repositorio


class RepositorioAutores(Repositorio[Autor]):
    modelo = Autor

    def listar(self) -> list[Autor]:
        consulta = select(Autor)
        return list(self.session.exec(consulta).all())
