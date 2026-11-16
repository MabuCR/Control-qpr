"""Ingesta de la hoja MAPA del Excel 'Control QPR asignados.xlsx'.

La hoja MAPA es un plano visual: 32 'estaciones' organizadas en una
grilla de 8 filas x 4 columnas de bloques. Cada bloque ocupa 3 filas x
3 columnas de celdas:

    [Nombre]  [Control]  [Numero de estacion]   <- solo la 1ra fila del bloque trae el numero
    [Nombre]  [Control]  (vacio)
    [Nombre]  [Control]  (vacio)

O sea, cada estacion puede tener hasta 3 personas asignadas, cada una
con su propio codigo de control (letras tipo FRCT, o a veces un numero
suelto).
"""
from __future__ import annotations

from pathlib import Path

import openpyxl

COL_STARTS = (2, 5, 8, 11)  # columnas B, E, H, K (1-indexed)
ROW_STARTS = (2, 5, 8, 11, 14, 17, 20, 23)  # filas donde arranca cada fila de bloques
FILAS_POR_BLOQUE = 3


def parsear_mapa(ruta_excel: Path | str) -> list[dict]:
    wb = openpyxl.load_workbook(ruta_excel, data_only=True)
    ws = wb["MAPA"]

    registros: list[dict] = []
    for fila_inicio in ROW_STARTS:
        for col_inicio in COL_STARTS:
            estacion = ws.cell(row=fila_inicio, column=col_inicio + 2).value
            if estacion is None:
                continue
            for posicion in range(FILAS_POR_BLOQUE):
                fila = fila_inicio + posicion
                nombre = ws.cell(row=fila, column=col_inicio).value
                control = ws.cell(row=fila, column=col_inicio + 1).value
                if not nombre:
                    continue
                nombre_limpio = str(nombre).strip()
                control_limpio = str(control).strip() if control is not None else None
                registros.append(
                    {
                        "nombre": nombre_limpio,
                        "control": control_limpio,
                        "estacion": int(estacion),
                        "posicion": posicion,
                    }
                )
    return registros


if __name__ == "__main__":
    import sys

    from app.db import init_db, reemplazar_asignaciones

    ruta = sys.argv[1] if len(sys.argv) > 1 else "Control QPR asignados.xlsx"
    registros = parsear_mapa(ruta)
    init_db()
    reemplazar_asignaciones(registros)
    print(f"Listo: {len(registros)} asignaciones cargadas desde {ruta}")
