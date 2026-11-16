# Control QPR asignados

App movil sencilla de **solo consulta**: quien tiene asignado cual radio
QPR (codigo de control) y en que estacion del plano, segun la hoja
**MAPA** del Excel `Control QPR asignados.xlsx`.

Se ignoraron a proposito las hojas `Hoja1` y `Hoja2` del Excel original
-- la fuente de verdad acordada con el dueno de los datos es la hoja
MAPA.

## Que resuelve

- Buscar por **nombre**, **codigo de control** (ej. `FRCT`) o **numero
  de estacion**.
- Cada estacion del plano puede tener hasta 3 personas asignadas; al
  buscar a alguien tambien se muestra con quien comparte estacion.
- Boton de **camara**: en el celular, toma una foto del gafete/etiqueta
  y usa OCR (Tesseract.js, corre en el navegador, nada se sube a
  ningun servidor) para autocompletar la busqueda. No hay codigos de
  barras en los gafetes, solo texto, por eso se usa OCR y no un lector
  de barras.

## Como correrlo

```bash
cd control-qpr
uv run --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple --allow-insecure-host pypi.ci.artifacts.walmart.com -m app.ingest "data/Control QPR asignados.xlsx"
uv run --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple --allow-insecure-host pypi.ci.artifacts.walmart.com uvicorn app.main:app --host 0.0.0.0 --port 8731
```

Abrir en el celular (misma red/VPN que la compu que corre el servidor):

```
http://<IP-de-tu-compu>:8731
```

## Actualizar los datos

Cuando cambie el Excel (nuevas asignaciones, estaciones, etc.), solo
hay que reemplazar `data/Control QPR asignados.xlsx` y volver a correr
el comando de `app.ingest` de arriba -- reconstruye la base desde cero
a partir de la hoja MAPA.

## Estructura

```
app/
  db.py        # SQLite: esquema + busqueda
  ingest.py    # Parser de la hoja MAPA -> registros planos
  main.py      # FastAPI: pagina + endpoint /buscar (HTMX)
  templates/   # HTML + Tailwind (CDN) + HTMX + Tesseract.js (CDN)
data/
  Control QPR asignados.xlsx   # NO se sube a git (datos de personas)
  qpr.db                        # NO se sube a git (se regenera con ingest)
```

## Por que es "solo consulta" por ahora

Se decidio asi a proposito (YAGNI): hoy el pedido real es poder ver
rapido desde el celular quien tiene que radio. Si mas adelante hace
falta marcar "entregado" o "devuelto" desde la app, se agrega ese flujo
despues, sin tener que rehacer nada de lo ya construido.
