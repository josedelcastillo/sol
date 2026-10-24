# Guía del alumno — Lab 1: Integración Continua con GitHub


## Antes de empezar

**Qué vas a construir.** Un repositorio en GitHub donde ningún cambio de código puede fusionarse a la rama principal si falla un test, si usa una librería con vulnerabilidad conocida o si contiene una credencial. El repositorio de partida contiene una API de inventario con un bug, una librería vulnerable y una credencial expuesta. Al final de la sesión, el mecanismo que construyes detecta las tres cosas.

**Requisitos.**

- Cuenta de GitHub con sesión iniciada en el navegador.
- Para explorar el proyecto puedes hacerlo con Visual Studio en tu computadora o con Codespaces (GitHub) en el navegador. Si usas Codespaces, asegúrate de que tu cuenta de GitHub tenga acceso a esta funcionalidad.

**Convenciones de esta guía.**

- `texto en código` es algo que se escribe o se hace clic tal cual.
- `<apellido>` se reemplaza por tu apellido en minúsculas, sin tildes.
- Cada paso termina con una verificación. No avances si la verificación no se cumple: escribe en el chat de Zoom el número del paso y qué ves para poder ayudarte.
- Los comandos se escriben en tu terminal o en la terminal de Codespaces (`Terminal → New Terminal`), uno por línea, Enter después de cada uno.

## Paso 1 — Crear tu repositorio

1. Abre el repositorio plantilla: `https://github.com/josedelcastillo/PUCP-LAB-M1`.
2. Clic en `Use this template` → `Create a new repository`.
3. Repository name: `PUCP-LAB-M1-<apellido>`. Visibilidad: `Public`.
4. Clic en `Create repository`.

**Verificación.** Tu navegador muestra `https://github.com/<tu-usuario>/PUCP-LAB-M1-<apellido>` con los archivos `app/`, `tests/`, `Makefile` y `README.md`.

## Paso 2 — Abrir el entorno y correr los tests

1. Clic en el botón verde `Code` → pestaña `Codespaces` → `Create codespace on main`. Espera 1–2 minutos.
2. En la terminal:

```bash
make install
make test
```

**Verificación.** La salida termina con una línea en rojo que dice `1 failed` y nombra el test `test_withdraw_exact_stock`. Lee el mensaje de error completo: dice qué esperaba el test y qué devolvió la aplicación.

## Paso 3 — Conocer el pipeline y ponerlo en marcha

El repositorio ya trae un pipeline en `.github/workflows/ci.yml`. No tienes que escribirlo desde cero: en este paso lo lees y lo haces correr. En los pasos 6 y 7 le agregarás bloques ya preparados.

1. En el explorador de archivos (barra izquierda), abre `.github/workflows/ci.yml`. Cada parte tiene un comentario que explica qué hace. Resumen:

| Parte del archivo | Qué significa |
| --- | --- |
| `on: pull_request` | El pipeline corre cada vez que se abre o actualiza un PR hacia `main` |
| `jobs:` → `build-and-test:` | Un job: un grupo de pasos que corre en una máquina de GitHub |
| `runs-on: ubuntu-latest` | La máquina donde corre el job: un Linux que GitHub crea y destruye en cada ejecución |
| `steps:` | Los pasos, en orden. Si uno falla, los siguientes no corren y el job queda en rojo |
| `uses:` | Reutiliza una acción ya publicada, por ejemplo descargar el código o instalar Python |
| `run:` | Ejecuta un comando, igual que si lo escribieras en tu terminal |

2. El pipeline solo corre cuando hay un PR, y un PR necesita al menos un cambio. En la terminal, crea tu rama:

```bash
git checkout -b feature/ci
```

3. Abre `README.md`. Debajo del título `# PUCP-LAB-M1` agrega una línea con `Alumno: <tu nombre completo>`. Guarda (`Ctrl+S`).
4. En la terminal:

```bash
git add .
git commit -m "docs: agregar nombre del alumno"
git push -u origin feature/ci
```

**Verificación.** La terminal termina mostrando una línea con `Create a pull request for 'feature/ci'` y una URL.

## Paso 4 — Abrir el pull request

1. Vuelve a la pestaña del navegador con tu repositorio en GitHub y recárgala.
2. Aparece un aviso amarillo `feature/ci had recent pushes` → clic en `Compare & pull request`.
3. Título: `CI: lint y tests`. Clic en `Create pull request`.
4. Espera 1–2 minutos. En la parte baja del PR aparece el check `build-and-test`.

**Verificación.** El check `build-and-test` está en rojo con una X. Clic en `Details` y ubica el paso que falló: es el paso `pytest`. Confirma que es el mismo test del Paso 2.

## Paso 5 — Corregir el bug

1. Vuelve a Codespaces. Abre `app/inventory.py`.
2. Ubica la función `withdraw`. Encuentra la comparación entre la cantidad pedida y el stock disponible: usa `>=`. Cámbiala por `>`.
3. Guarda. En la terminal:

```bash
make test
```

Todos los tests deben pasar. Luego:

```bash
git add .
git commit -m "fix: permitir retirar exactamente el stock disponible"
git push
```

**Verificación.** En el PR, tras 1–2 minutos, el check `build-and-test` está en verde. No modificaste ningún archivo dentro de `tests/`.

## Paso 6 — Detectar librerías vulnerables

1. Abre `.github/workflows/ci.yml`. Ve al final del archivo, después de la última línea (`- run: pytest ...`), y pega el segundo job. La palabra `security:` debe quedar exactamente debajo de `build-and-test:`, con dos espacios al inicio. La indentación importa: usa espacios, nunca tabulaciones.

```yaml
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pip-audit
      - run: pip-audit -r requirements.txt
```

2. Guarda. En la terminal:

```bash
git add .
git commit -m "ci: analisis de dependencias"
git push
```

**Verificación.** En el PR aparece un segundo check `security`, en rojo. En `Details`, el paso `pip-audit` lista la librería `requests` versión `2.25.1` con uno o más identificadores `CVE-` o `PYSEC-` y, en la columna `Fix Versions`, la versión que corrige. También aparecen `idna` y `urllib3`: no están en `requirements.txt`, llegan como dependencias de `requests` y se corrigen al actualizarla.

3. Abre `requirements.txt`. Reemplaza `requests==2.25.1` por `requests==` seguido de la versión indicada en `Fix Versions` para `requests` (la más alta si hay varias). No agregues `idna` ni `urllib3`.
4. Guarda. Commit con mensaje `fix: actualizar requests` y push.

**Verificación.** El check `security` está en verde.

## Paso 7 — Detectar credenciales en el código

1. Abre `app/config.py`. Observa la línea `INVENTORY_API_KEY = "ghp_..."`. Es una credencial escrita directamente en el código.
2. En `ci.yml`, al final del job `security`, agrega:

```yaml
      - name: gitleaks
        run: |
          curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v8.28.0/gitleaks_8.28.0_linux_x64.tar.gz | tar -xz gitleaks
          ./gitleaks dir . --redact --verbose
```

`gitleaks dir .` revisa los archivos tal como están en la rama del PR, así que el check se pone en verde cuando la credencial sale del código. Que siga existiendo en el historial de git es tema de la pregunta de cierre 2.

3. Guarda. Commit con mensaje `ci: deteccion de secretos` y push.

**Verificación.** El check `security` está en rojo. En `Details`, el paso `gitleaks` reporta un hallazgo en `app/config.py` con el tipo `github-pat`.

4. En GitHub, pestaña `Settings` del repositorio → menú izquierdo `Secrets and variables` → `Actions` → `New repository secret`. Name: `INVENTORY_API_KEY`. Secret: cualquier texto, por ejemplo `clave-de-prueba`. Clic en `Add secret`. Aquí vive el valor real de la clave: el código lo leerá de una variable de entorno cuando la aplicación se despliegue. El pipeline de este laboratorio no lo necesita.
5. En Codespaces, abre `app/config.py`. Reemplaza la línea de `INVENTORY_API_KEY` por:

```python
import os

INVENTORY_API_KEY = os.getenv("INVENTORY_API_KEY", "")
```

Si `import os` ya existe al inicio del archivo, no lo dupliques.

6. Guarda. En la terminal `make test` debe pasar. Commit con mensaje `fix: leer api key desde variable de entorno` y push.

**Verificación.** Ambos checks, `build-and-test` y `security`, están en verde.

Si algún check falla por un error de formato del archivo (por ejemplo `Invalid workflow file`), compara tu `ci.yml` con la versión completa esperada en este punto:

```yaml
# Pipeline de integración continua.
# GitHub lo ejecuta cada vez que se abre o actualiza un pull request hacia main.
name: CI
on:
  pull_request:
    branches: [main]
jobs:
  # Job 1: revisa el estilo del código (lint) y ejecuta los tests.
  build-and-test:
    runs-on: ubuntu-latest # máquina virtual de GitHub donde corre el job
    steps:
      # Descarga el código de la rama del pull request.
      - uses: actions/checkout@v4
      # Instala Python 3.12 y guarda en caché las librerías descargadas.
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      # Instala las librerías de la aplicación y de desarrollo.
      - run: pip install -r requirements.txt -r requirements-dev.txt
      # Lint: falla si el código no respeta el estándar del equipo.
      - run: ruff check .
      # Tests: falla si un test no pasa o si la cobertura es menor a 80 %.
      - run: pytest --cov=app --cov-fail-under=80
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pip-audit
      - run: pip-audit -r requirements.txt
      - name: gitleaks
        run: |
          curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v8.28.0/gitleaks_8.28.0_linux_x64.tar.gz | tar -xz gitleaks
          ./gitleaks dir . --redact --verbose
```

## Paso 8 — Proteger la rama principal

1. En GitHub, `Settings` → menú izquierdo `Branches` → `Add classic branch protection rule`.
2. Branch name pattern: `main`.
3. Marca `Require a pull request before merging`. Debajo se marca sola la opción `Require approvals`: **desmárcala**. Trabajas sin compañero en tu repositorio y GitHub no permite aprobar tu propio PR; si la dejas marcada, el merge queda bloqueado aunque todo esté en verde.
4. Marca `Require status checks to pass before merging` y, debajo, `Require branches to be up to date before merging`. En el buscador escribe `build` y selecciona `build-and-test`; luego escribe `security` y selecciónalo.
5. Más abajo, marca `Do not allow bypassing the above settings`. Sin esta opción, como eres administrador del repositorio, GitHub te ofrece fusionar saltándote la regla.
6. Clic en `Create` al final de la página.

**Verificación.** Vuelve al PR. El botón `Merge pull request` está verde y habilitado.

7. Prueba que el mecanismo bloquea. En Codespaces, abre `app/inventory.py` y vuelve a cambiar `>` por `>=`. Guarda, commit con mensaje `test: romper a proposito` y push.

**Verificación.** Tras 1–2 minutos, `build-and-test` está en rojo y el botón de merge aparece deshabilitado con el texto `Merging is blocked`.

8. Deshaz el cambio: vuelve a poner `>`. Guarda, commit con mensaje `fix: restaurar correccion` y push.
9. Cuando ambos checks estén en verde, clic en `Merge pull request` → `Confirm merge`.

**Verificación.** La rama `main` contiene `ci.yml`, el bug corregido, `requests` actualizado y sin credencial en `config.py`.

## Paso 9 — Opcional, si terminaste antes

1. `Settings` → `Code security` → sección `Code scanning` → `CodeQL analysis` → `Set up` → `Default`. Clic en `Enable CodeQL`. Los resultados aparecen en la pestaña `Security` en unos minutos.
2. En Codespaces, crea el archivo `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: pip
    directory: "/"
    schedule:
      interval: weekly
```

3. Commit en una rama nueva, PR y merge. En los minutos siguientes GitHub abre pull requests automáticos con actualizaciones de librerías.

## Preguntas de cierre

Para responder en voz alta al final de la sesión.

1. Si el test hubiera estado en verde desde el inicio, ¿cuándo se habría descubierto el bug y quién habría pagado el costo?
2. La credencial se movió a un GitHub Secret. ¿Sigue existiendo en algún lugar del repositorio? ¿Qué debería hacer la empresa con esa credencial?
3. ¿Qué parte de lo que hiciste hoy le explicarías a un gerente de finanzas y con qué número?

## Glosario

| Término | Significado en este laboratorio |
| --- | --- |
| Repositorio | Carpeta con el código y todo su historial de cambios, alojada en GitHub |
| Commit | Un cambio guardado con un mensaje que lo describe |
| Rama (branch) | Una copia del código donde se trabaja sin afectar la principal (`main`) |
| Pull request (PR) | Propuesta de llevar los cambios de una rama a `main`; otros la revisan antes de aceptarla |
| Merge | Aceptar el PR: los cambios pasan a `main` |
| Test | Código que verifica que otro código cumple una regla; pasa (verde) o falla (rojo) |
| Workflow | Archivo YAML que describe qué ejecutar automáticamente y cuándo |
| Job | Grupo de pasos dentro de un workflow; los jobs corren en paralelo salvo que se indique lo contrario |
| Check | Resultado de un job mostrado en el PR: verde o rojo |
| Lint | Revisión automática de estilo y errores comunes en el código |
| Cobertura | Porcentaje del código que los tests ejecutan |
| CVE | Identificador público de una vulnerabilidad conocida en un software |
| Secreto | Credencial, token o clave; nunca se escribe en el código |
| Branch protection | Regla que impide fusionar a `main` sin cumplir condiciones |
