# PUCP-LAB-M1

API de inventario en memoria construida con FastAPI y Python 3.12.

## Qué hace la API

Mantiene en memoria una lista de tres items precargados y permite consultar y retirar stock.

| Método | Ruta                   | Descripción                                                    |
|--------|------------------------|----------------------------------------------------------------|
| GET    | `/health`              | Estado del servicio: `{"status": "ok"}`                        |
| GET    | `/items`               | Lista de items con `id`, `name` y `qty`                        |
| POST   | `/items/{id}/withdraw` | Retira stock con el body `{"qty": 2}` y devuelve el item actualizado. Responde 400 si la cantidad supera el stock y 404 si el item no existe |
| GET    | `/debug/config`        | Indica si la configuración del servicio está completa: `{"api_key_configured": true}` |

Cuando el stock de un item queda bajo, la API envía un aviso a la URL definida en la variable de entorno `NOTIFY_WEBHOOK_URL`, si existe.

## Cómo correrla

Requisitos: Python 3.12 y `make`. Se recomienda trabajar dentro de un entorno virtual:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Comandos:

```bash
make install   # instala las dependencias de la aplicación y de desarrollo
make run       # levanta la API en http://localhost:8000 con recarga automática
make test      # ejecuta los tests con reporte de cobertura
make lint      # revisa el código con ruff
```

La documentación interactiva queda disponible en `http://localhost:8000/docs`.

Ejemplo:

```bash
curl http://localhost:8000/items
curl -X POST http://localhost:8000/items/1/withdraw \
  -H "Content-Type: application/json" -d '{"qty": 2}'
```

El repositorio incluye un Dev Container: al abrirlo, el entorno ejecuta `make install` y expone el puerto 8000.

## Estructura de carpetas

```
.
├── app/
│   ├── __init__.py
│   ├── main.py          # rutas FastAPI
│   ├── inventory.py     # lógica del inventario
│   ├── config.py        # configuración
│   └── notify.py        # avisos de stock bajo
├── tests/
│   └── test_api.py      # tests de la API
├── .devcontainer/
│   └── devcontainer.json
├── .github/workflows/
│   └── ci.yml           # pipeline de integración continua
├── Makefile
├── pyproject.toml       # configuración de ruff y pytest
├── requirements.txt     # dependencias de la aplicación
└── requirements-dev.txt # dependencias de desarrollo
```
