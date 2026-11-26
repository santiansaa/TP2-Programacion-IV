class ErrorBiblioteca(Exception):
    pass


class NoEncontrado(ErrorBiblioteca):
    pass


class Conflicto(ErrorBiblioteca):
    pass


class Prohibido(ErrorBiblioteca):
    pass
