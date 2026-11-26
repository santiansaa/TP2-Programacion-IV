from models.autor import Autor, AutorActualizar, AutorCrear
from repositories.autores import RepositorioAutores
from services.errores import NoEncontrado


class ServicioAutores:
    def __init__(self, repo: RepositorioAutores):
        self.repo = repo

    def crear_autor(self, datos: AutorCrear) -> Autor:
        with self.repo.escritura():
            return self.repo.guardar(Autor.model_validate(datos))

    def modificar_autor(self, id: int, datos: AutorActualizar) -> Autor:
        with self.repo.escritura():
            autor = self.obtener_autor(id)
            autor.sqlmodel_update(datos.model_dump())
            return self.repo.guardar(autor)

    def eliminar_autor(self, id: int) -> None:
        with self.repo.escritura():
            self.repo.eliminar(self.obtener_autor(id))

    def obtener_autor(self, id: int) -> Autor:
        autor = self.repo.buscar(id)
        if autor is None:
            raise NoEncontrado("Autor no encontrado")
        return autor

    def listar_autores(self) -> list[Autor]:
        return self.repo.listar()
