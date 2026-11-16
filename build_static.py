"""Genera una pagina HTML standalone (sin backend) para GitHub Pages.

Reutiliza app.ingest.parsear_mapa (misma fuente de verdad que usa la
version con servidor FastAPI) para no duplicar la logica de lectura
del Excel. Los datos quedan embebidos directo en el HTML como JSON --
son apenas ~85 registros, no hace falta comprimir nada.

Uso: python build_static.py "data/Control QPR asignados.xlsx"
Escribe index.html en la raiz del proyecto (lo que sirve GitHub Pages).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from app.ingest import parsear_mapa

BASE_DIR = Path(__file__).resolve().parent
OUT_PATH = BASE_DIR / "index.html"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>Control QPR asignados</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
    input[type="text"], input[type="search"] { font-size: 16px; }
    @keyframes parpadeo { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
    .resaltado { animation: parpadeo 1s ease-in-out infinite; background: #fef3c7 !important; border-color: #fbbf24 !important; }
</style>
</head>
<body class="bg-slate-100 min-h-screen">
<header class="bg-blue-700 text-white px-4 py-3 shadow sticky top-0 z-10">
    <h1 class="text-lg font-bold">Control QPR asignados</h1>
    <p class="text-blue-100 text-xs">Consulta rapida por nombre, control o estacion (sin servidor)</p>
</header>
<main class="max-w-xl mx-auto p-4">

    <div class="bg-white rounded-xl shadow p-4 mb-4">
        <label for="buscador" class="block text-sm font-semibold text-slate-700 mb-2">
            Nombre, codigo de control o numero de estacion
        </label>
        <div class="flex gap-2">
            <input id="buscador" type="search" placeholder="Ej: FRCT, 12, Juan Gomez..." autocomplete="off"
                class="flex-1 border border-slate-300 rounded-lg px-3 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <label class="flex items-center justify-center w-14 bg-blue-600 active:bg-blue-700 text-white rounded-lg cursor-pointer">
                <input id="camara" type="file" accept="image/*" capture="environment" class="hidden">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 7h3l2-2h6l2 2h3a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1z"/>
                    <circle cx="12" cy="13" r="3.5"/>
                </svg>
            </label>
        </div>
        <p id="ocr-estado" class="text-xs text-slate-400 mt-2"></p>
    </div>

    <div class="bg-white rounded-xl shadow p-2 mb-4">
        <h2 class="text-sm font-semibold text-slate-700 mb-2">Mueble de radios</h2>
        <div id="mueble" class="grid grid-cols-4 gap-1"></div>
    </div>

    <div id="resultados">
        <p class="text-slate-400 text-sm text-center mt-8" id="placeholder-inicial"></p>
    </div>
</main>

<script src="https://unpkg.com/tesseract.js@5/dist/tesseract.min.js"></script>
<script>
    const DATOS = __DATOS_JSON__;

    const porEstacion = {};
    let totalEstaciones = 0;
    DATOS.forEach((r) => {
        (porEstacion[r.estacion] ||= []).push(r);
        totalEstaciones = Math.max(totalEstaciones, r.estacion);
    });

    document.getElementById("placeholder-inicial").textContent =
        DATOS.length + " asignaciones cargadas. Escribe algo arriba para buscar.";

    function pintarMueble() {
        const cont = document.getElementById("mueble");
        let html = "";
        for (let n = 1; n <= totalEstaciones; n++) {
            const ocupantes = porEstacion[n] || [];
            html += `<div id="casillero-${n}" class="casillero rounded border border-slate-200 bg-slate-50 flex flex-col items-center justify-start gap-0.5 p-0.5 min-h-[2.75rem]">`;
            html += `<span class="text-[8px] font-bold text-slate-400 leading-none">${n}</span>`;
            if (ocupantes.length === 0) {
                html += `<span class="text-[6.5px] text-slate-300">vacio</span>`;
            } else {
                ocupantes.forEach((p) => {
                    html += `<span class="text-[6.5px] leading-[1.1] text-slate-600 text-center break-words w-full">${p.nombre}</span>`;
                });
            }
            html += `</div>`;
        }
        cont.innerHTML = html;
    }

    function resaltarEstaciones(estaciones) {
        document.querySelectorAll(".casillero").forEach((el) => el.classList.remove("resaltado"));
        let primero = null;
        estaciones.forEach((n) => {
            const el = document.getElementById("casillero-" + n);
            if (el) {
                el.classList.add("resaltado");
                primero = primero || el;
            }
        });
        if (primero) primero.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    function tarjetaResultado(fila, companeros) {
        let html = `<div class="bg-white rounded-xl shadow p-4 border-l-4 border-blue-600">`;
        html += `<div class="flex items-center justify-between">`;
        html += `<h2 class="font-bold text-slate-800">${fila.nombre}</h2>`;
        html += `<span class="bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-1 rounded-full">Estacion ${fila.estacion}</span>`;
        html += `</div>`;
        html += `<p class="text-sm text-slate-500 mt-1">Control: <span class="font-mono font-semibold text-slate-700">${fila.control || "sin codigo"}</span></p>`;
        if (companeros.length) {
            html += `<div class="mt-3 pt-3 border-t border-slate-100"><p class="text-xs text-slate-400 mb-1">Comparte estacion con:</p><ul class="text-sm text-slate-600 space-y-0.5">`;
            companeros.forEach((c) => {
                html += `<li>${c.nombre} -- control ${c.control || "sin codigo"}</li>`;
            });
            html += `</ul></div>`;
        }
        html += `</div>`;
        return html;
    }

    function buscar() {
        const q = document.getElementById("buscador").value.trim().toLowerCase();
        const cont = document.getElementById("resultados");
        if (!q) {
            cont.innerHTML = `<p class="text-slate-400 text-sm text-center mt-8">${DATOS.length} asignaciones cargadas. Escribe algo arriba para buscar.</p>`;
            resaltarEstaciones([]);
            return;
        }
        const matches = DATOS.filter((r) =>
            r.nombre.toLowerCase().includes(q) ||
            (r.control || "").toLowerCase().includes(q) ||
            String(r.estacion) === q
        );
        if (!matches.length) {
            cont.innerHTML = `<p class="text-slate-400 text-sm text-center mt-8">Sin resultados para "${q}".</p>`;
            resaltarEstaciones([]);
            return;
        }
        let html = `<div class="space-y-3">`;
        matches.forEach((fila) => {
            const companeros = (porEstacion[fila.estacion] || []).filter((p) => p !== fila);
            html += tarjetaResultado(fila, companeros);
        });
        html += `</div>`;
        cont.innerHTML = html;
        resaltarEstaciones([...new Set(matches.map((m) => m.estacion))]);
    }

    document.getElementById("buscador").addEventListener("input", buscar);

    const inputCamara = document.getElementById("camara");
    const buscador = document.getElementById("buscador");
    const estado = document.getElementById("ocr-estado");

    inputCamara.addEventListener("change", async (evento) => {
        const archivo = evento.target.files[0];
        if (!archivo) return;
        estado.textContent = "Leyendo texto de la foto...";
        try {
            const resultado = await Tesseract.recognize(archivo, "eng", { logger: () => {} });
            const texto = resultado.data.text || "";
            const limpio = texto.replace(/[^A-Za-z0-9]/g, " ").trim().split(/\\s+/)[0] || "";
            if (limpio) {
                buscador.value = limpio;
                buscar();
                estado.textContent = "Detectado: " + limpio + " (podes corregirlo a mano si hizo falta)";
            } else {
                estado.textContent = "No se detecto texto claro, intenta con mas luz o mas cerca.";
            }
        } catch (error) {
            estado.textContent = "No se pudo leer la foto, intenta de nuevo.";
        }
        inputCamara.value = "";
    });

    pintarMueble();
</script>
</body>
</html>
"""


def construir(ruta_excel: str) -> None:
    registros = parsear_mapa(ruta_excel)
    html = HTML_TEMPLATE.replace("__DATOS_JSON__", json.dumps(registros, ensure_ascii=False))
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"Listo: {OUT_PATH} generado con {len(registros)} registros embebidos.")


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "data/Control QPR asignados.xlsx"
    construir(ruta)
