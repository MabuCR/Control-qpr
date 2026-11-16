"""Acceso a la base de datos SQLite para Control QPR asignados.

El esquema es deliberadamente chiquito: una sola tabla `asignaciones`
poblada a partir de la hoja MAPA del Excel. Nada de ORMs pesados,
solo sqlite3 de la stdlib -- YAGNI.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "qpr.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS asignaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    control TEXT,
    estacion INTEGER NOT NULL,
    posicion INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_nombre ON asignaciones (nombre);
CREATE INDEX IF NOT EXISTS idx_control ON asignaciones (control);
CREATE INDEX IF NOT EXISTS idx_estacion ON asignaciones (estacion);
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def reemplazar_asignaciones(registros: list[dict]) -> None:
    """Borra todo y vuelve a insertar -- la fuente de verdad es el Excel."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM asignaciones")
        conn.executemany(
            """
            INSERT INTO asignaciones (nombre, control, estacion, posicion)
            VALUES (:nombre, :control, :estacion, :posicion)
            """,
            registros,
        )
        conn.commit()
    finally:
        conn.close()


def buscar(termino: str) -> list[sqlite3.Row]:
    """Busca por nombre, control o estacion. Vacio -> sin resultados."""
    termino = (termino or "").strip()
    if not termino:
        return []
    conn = get_connection()
    try:
        like = f"%{termino}%"
        filas = conn.execute(
            """
            SELECT id, nombre, control, estacion, posicion
            FROM asignaciones
            WHERE nombre LIKE ? COLLATE NOCASE
               OR control LIKE ? COLLATE NOCASE
               OR CAST(estacion AS TEXT) = ?
            ORDER BY estacion, posicion
            """,
            (like, like, termino),
        ).fetchall()
        return filas
    finally:
        conn.close()


def companeros_de_estacion(estacion: int, excluir_id: int) -> list[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT id, nombre, control, estacion, posicion
            FROM asignaciones
            WHERE estacion = ? AND id != ?
            ORDER BY posicion
            """,
            (estacion, excluir_id),
        ).fetchall()
    finally:
        conn.close()


def total_registros() -> int:
    conn = get_connection()
    try:
        row = conn.execute("SELECT COUNT(*) AS n FROM asignaciones").fetchone()
        return row["n"]
    finally:
        conn.close()
