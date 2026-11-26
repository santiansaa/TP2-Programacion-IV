

from contextlib import asynccontextmanager
from routers.autores import router as autores_router
from routers.libros import router as libros_router
from routers.socios import router as socios_router
from routers.prestamos import router as prestamos_router
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from services.errores import Conflicto, ErrorBiblioteca, NoEncontrado, Prohibido

import models
from database import crear_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_db()
    yield


app = FastAPI(
    title="Sistema de Biblioteca",
    lifespan=lifespan
)


@app.exception_handler(ErrorBiblioteca)
async def responder_error(request: Request, error: ErrorBiblioteca):
    codigos = {NoEncontrado: 404, Conflicto: 409, Prohibido: 403}
    return JSONResponse(status_code=codigos[type(error)], content={"detail": str(error)})


app.include_router(autores_router)
app.include_router(libros_router)
app.include_router(socios_router)
app.include_router(prestamos_router)
@app.get("/")
def inicio():
    return {"mensaje": "API de Biblioteca funcionando"}
