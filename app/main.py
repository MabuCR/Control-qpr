"""Control QPR asignados -- consulta movil de radios por estacion.

App chiquita y practica: buscas por nombre, codigo de control o numero
de estacion (o le apuntas la camara) y te dice quien tiene que radio y
en que estacion del plano MAPA.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db import (
    buscar,
    companeros_de_estacion,
    init_db,
    obtener_mueble,
    total_registros,
)

app = FastAPI(title="Control QPR asignados")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    mueble = obtener_mueble()
    total_estaciones = max(mueble.keys()) if mueble else 0
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "total": total_registros(),
            "mueble": mueble,
            "rango_estaciones": range(1, total_estaciones + 1),
        },
    )


@app.get("/buscar", response_class=HTMLResponse)
def buscar_endpoint(request: Request, q: str = ""):
    filas = buscar(q)
    resultados = []
    for fila in filas:
        companeros = companeros_de_estacion(fila["estacion"], fila["id"])
        resultados.append({"fila": fila, "companeros": companeros})

    estaciones_encontradas = sorted({fila["estacion"] for fila in filas})

    return templates.TemplateResponse(
        request,
        "partials/resultados.html",
        {
            "q": q,
            "resultados": resultados,
            "estaciones_encontradas": estaciones_encontradas,
        },
    )
