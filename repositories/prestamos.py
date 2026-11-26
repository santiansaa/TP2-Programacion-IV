from sqlmodel import select

from models.prestamo import Prestamo
from repositories.persistencia import Repositorio


class RepositorioPrestamos(Repositorio[Prestamo]):
    modelo = Prestamo

    def listar_por_socio(self, socio_id: int, activos: bool) -> list[Prestamo]:
        consulta = select(Prestamo).where(Prestamo.socio_id == socio_id)
        if activos:
            consulta = consulta.where(Prestamo.fecha_devolucion.is_(None))
        return list(self.session.exec(consulta).all())
