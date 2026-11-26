from datetime import date, timedelta

from models.prestamo import Prestamo, PrestamoCrear
from repositories.libros import RepositorioLibros
from repositories.prestamos import RepositorioPrestamos
from repositories.socios import RepositorioSocios
from services.errores import Conflicto, NoEncontrado, Prohibido


class ServicioPrestamos:
    def __init__(self, prestamos: RepositorioPrestamos, libros: RepositorioLibros,
                 socios: RepositorioSocios):
        self.prestamos = prestamos
        self.libros = libros
        self.socios = socios

    def crear_prestamo(self, datos: PrestamoCrear) -> Prestamo:
        with self.prestamos.escritura():
            socio = self.socios.buscar(datos.socio_id)
            libro = self.libros.buscar(datos.libro_id)
            if socio is None or libro is None:
                raise NoEncontrado("Socio o libro no encontrado")
            if not socio.activo:
                raise Prohibido("El socio esta inactivo")
            if len(self.prestamos.listar_por_socio(datos.socio_id, activos=True)) >= 3:
                raise Conflicto("El socio ya tiene 3 prestamos activos")
            if libro.stock <= 0:
                raise Conflicto("No hay stock disponible")

            hoy = date.today()
            prestamo = Prestamo(**datos.model_dump(), fecha_prestamo=hoy,
                                fecha_vencimiento=hoy + timedelta(days=14))
            libro.stock -= 1
            self.libros.guardar(libro)
            return self.prestamos.guardar(prestamo)

    def devolver_prestamo(self, id: int) -> Prestamo:
        with self.prestamos.escritura():
            prestamo = self.prestamos.buscar(id)
            if prestamo is None:
                raise NoEncontrado("Prestamo no encontrado")
            if prestamo.fecha_devolucion is not None:
                raise Conflicto("El prestamo ya fue devuelto")
            libro = self.libros.buscar(prestamo.libro_id)
            if libro is None:
                raise NoEncontrado("Libro no encontrado")
            hoy = date.today()
            prestamo.fecha_devolucion = hoy
            prestamo.multa = max((hoy - prestamo.fecha_vencimiento).days, 0) * 100
            libro.stock += 1
            self.libros.guardar(libro)
            return self.prestamos.guardar(prestamo)

    def obtener_prestamos_socio(self, id: int, activos: bool) -> list[Prestamo]:
        if self.socios.buscar(id) is None:
            raise NoEncontrado("Socio no encontrado")
        return self.prestamos.listar_por_socio(id, activos)
