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
python -m pytest tests/ --cov=models --cov=routers --cov=services --cov-report=term-missing
```

**Último resultado verificado:**
- 19 tests aprobados.
- 100 % de cobertura de `models/`, `routers/` y `services/`.
