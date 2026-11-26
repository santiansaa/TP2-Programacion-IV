from models.socio import Socio, SocioActualizar, SocioCrear
from repositories.socios import RepositorioSocios
from repositories.persistencia import RegistroReferenciado, ValorDuplicado
from services.errores import Conflicto, NoEncontrado


class ServicioSocios:
    def __init__(self, repo: RepositorioSocios):
        self.repo = repo

    def crear_socio(self, datos: SocioCrear) -> Socio:
        try:
            with self.repo.escritura():
                return self.repo.guardar(Socio.model_validate(datos))
        except ValorDuplicado as error:
            raise Conflicto("Email duplicado") from error

    def modificar_socio(self, id: int, datos: SocioActualizar) -> Socio:
        try:
            with self.repo.escritura():
                socio = self.obtener_socio(id)
                socio.sqlmodel_update(datos.model_dump())
                return self.repo.guardar(socio)
        except ValorDuplicado as error:
            raise Conflicto("Email duplicado") from error

    def eliminar_socio(self, id: int) -> None:
        try:
            with self.repo.escritura():
                self.repo.eliminar(self.obtener_socio(id))
        except RegistroReferenciado as error:
            raise Conflicto("El socio tiene historial de préstamos") from error

    def obtener_socio(self, id: int) -> Socio:
        socio = self.repo.buscar(id)
        if socio is None:
            raise NoEncontrado("Socio no encontrado")
        return socio

    def listar_socios(self) -> list[Socio]:
        return self.repo.listar()
