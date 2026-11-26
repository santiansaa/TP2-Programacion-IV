from models.libro import Libro, LibroActualizar, LibroCrear
from repositories.libros import RepositorioLibros
from repositories.autores import RepositorioAutores
from repositories.persistencia import RegistroReferenciado, ValorDuplicado
from services.errores import Conflicto, NoEncontrado


class ServicioLibros:
    def __init__(self, repo: RepositorioLibros, autores: RepositorioAutores):
        self.repo = repo
        self.autores = autores

    def crear_libro(self, datos: LibroCrear) -> Libro:
        try:
            with self.repo.escritura():
                return self.repo.guardar(Libro.model_validate(datos))
        except ValorDuplicado as error:
            raise Conflicto("ISBN duplicado") from error

    def modificar_libro(self, id: int, datos: LibroActualizar) -> Libro:
        try:
            with self.repo.escritura():
                libro = self.obtener_libro(id)
                libro.sqlmodel_update(datos.model_dump())
                return self.repo.guardar(libro)
        except ValorDuplicado as error:
            raise Conflicto("ISBN duplicado") from error

    def eliminar_libro(self, id: int) -> None:
        try:
            with self.repo.escritura():
                self.repo.eliminar(self.obtener_libro(id))
        except RegistroReferenciado as error:
            raise Conflicto("El libro tiene historial de préstamos") from error

    def obtener_libro(self, id: int) -> Libro:
        libro = self.repo.buscar(id)
        if libro is None:
            raise NoEncontrado("Libro no encontrado")
        return libro

    def listar_libros(self, disponibles: bool) -> list[Libro]:
        return self.repo.listar(disponibles)

    def asociar_autor(self, id: int, autor_id: int) -> None:
        with self.repo.escritura():
            libro = self.obtener_libro(id)
            autor = self.autores.buscar(autor_id)
            if autor is None:
                raise NoEncontrado("Autor no encontrado")
            self.repo.asociar(libro, autor)
