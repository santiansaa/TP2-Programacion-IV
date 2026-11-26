# TP2 - Sistema de Biblioteca

**Materia:** Programación IV  
**Lenguaje:** Python  
**Tecnologías:** FastAPI, SQLModel y SQLite

## Descripción

API REST para administrar una biblioteca, permitiendo registrar autores, libros, socios y gestionar préstamos y devoluciones.

## Funcionalidades

- CRUD de autores, libros y socios.
- Asociación de autores con libros.
- Consulta de libros disponibles.
- Registro de préstamos y devoluciones.
- Máximo de 3 préstamos activos por socio.
- Control de stock.
- Plazo de devolución de 14 días.
- Multa de $100 por día de atraso.
- Consulta de préstamos activos por socio.
- La baja de un libro o socio con historial de préstamos devuelve HTTP 409 y conserva el historial.

## Organización del código

- `routers/` recibe las peticiones HTTP, valida los datos de entrada con los esquemas y delega en los servicios.
- `services/` aplica las reglas del catálogo y los préstamos. Por ejemplo, al devolver un libro calcula la multa y repone el stock.
- `repositories/` consulta y modifica la base mediante SQLModel. Guarda el préstamo y el cambio de stock en una misma transacción.
- `dependencies.py` construye los servicios y sus repositorios con una sesión por petición.
- `models/` define las tablas, relaciones y esquemas de entrada y salida.
- `main.py` registra las rutas y traduce los errores de negocio a respuestas HTTP.

## Instalación

Crear un entorno virtual:

```powershell
python -m venv .venv
```

Activarlo en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

## Ejecutar la API

```powershell
python -m uvicorn main:app --reload
```

La API estará disponible en:

`http://127.0.0.1:8000`

También se pueden probar los endpoints desde Postman.

## Base de datos

Se utiliza SQLite mediante SQLModel.

El archivo `biblioteca.db` se genera automáticamente al iniciar la aplicación.

## Tests

Ejecutar las pruebas:

```powershell
python -m pytest tests/ -v
```

Ejecutar las pruebas con cobertura:

```powershell
python -m pytest tests/ --cov=models --cov=routers --cov=services --cov=repositories --cov=dependencies --cov=main --cov=database --cov-fail-under=80 --cov-report=term-missing
```

**Último resultado verificado:**
- 31 tests aprobados.
- 99,33 % de cobertura de líneas de la aplicación.
