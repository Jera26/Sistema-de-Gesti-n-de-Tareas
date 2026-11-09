# Resultados de pruebas

Entorno: Windows, Python 3.10.6, Django 4.1.5, pytest 9.2.0, pytest-django 4.14.0, selenium 4.52.0, Chrome 156.

## Etapa 1 – Restauración de rutas y línea base

### 1.1 Antes de restaurar `base/urls.py`

| Comando | Resultado |
|---|---|
| `python manage.py check` | Falla: `ModuleNotFoundError: No module named 'base.urls'` |
| `pytest -q --ignore=tests/e2e` | 14 fallidas, 1 aprobada (15 descubiertas) |

### 1.2 Después de restaurar `base/urls.py` (commit `6122a9f`)

| Comando | Resultado |
|---|---|
| `python manage.py check` | Sin problemas |
| `python manage.py makemigrations --check --dry-run` | Sin cambios pendientes |
| `pytest -q --ignore=tests/e2e` | **15/15 aprobadas** |

Verificación de rutas (cliente de pruebas de Django, usuario autenticado salvo login/register):

| Nombre | URL | Método | Estado |
|---|---|---|---|
| `login` | `/login/` | GET | 200 |
| `register` | `/register/` | GET | 200 |
| `tasks` | `/` | GET | 200 |
| `task` | `/task/1` | GET | 200 |
| `task-create` | `/create-task/` | GET | 200 |
| `task-update` | `/update-task/1/` | GET | 200 |
| `task-delete` | `/delete-task/1/` | GET | 200 |
| `logout` | `/logout/` | POST | 302 → `/login/` |

### 1.3 Archivos de prueba no descubiertos

`tests/test.models.py` y `tests/test.task.py` no cumplían el patrón `test_*.py` de `pytest.ini`.

- Renombrados con `git mv` a `tests/test_models.py` y `tests/test_task_extra.py`.
- `test_task_extra.py`: se agregaron los imports faltantes (`pytest`, `reverse`, `Task`) y `pytestmark = pytest.mark.django_db`. No se modificó ninguna aserción.

| Comando | Resultado |
|---|---|
| `pytest -q --ignore=tests/e2e` | **23/23 aprobadas** (8 pruebas recuperadas) |
| `pytest tests/e2e` (5 ejecuciones) | 4 ejecuciones 2/2; 1 ejecución con fallo intermitente en `test_flujo_completo_registro_y_tarea` (ver E-10) |

Las 4 pruebas de autorización de `test_tasks.py` (marcadas en un comentario como "HOY FALLAN") **pasan**: las vistas ya devuelven 404 para tareas ajenas porque filtran con `get_queryset(user=request.user)`.

### Defecto nuevo detectado

**E-10 (Baja, prueba inestable):** en `tests/e2e/test_acceptance.py`, `WebDriverWait(...).until(EC.url_contains(reverse("tasks")))` espera que la URL contenga `"/"`, condición que cualquier URL cumple de inmediato. La espera no sincroniza la redirección y `page_source` puede leerse antes de que cargue la lista. Corrección propuesta: esperar la URL exacta (`EC.url_to_be(live_server.url + reverse("tasks"))`) o la presencia del texto de la tarea.

## Etapa 2.1 – E-10: esperas de Selenium (commit `f2d23dc`)

`EC.url_contains("/")` se reemplazó por `EC.url_to_be(<URL de la lista>)` y `presence_of_element_located` del enlace de la tarea. El login incorrecto espera `ul.errorlist`. Modo headless opcional con `E2E_HEADLESS=1`. Sin esperas fijas.

| Pruebas | Ejecutadas | Aprobadas | Fallidas |
|---|---|---|---|
| E2E con ventana (5 repeticiones) | 10 | 10 | 0 |
| E2E headless (5 repeticiones) | 10 | 10 | 0 |

## Etapa 2.2 – Dependencias (commits `75352b0`, `2ee0fc0`)

Ver `docs/dependencias.md`. `pip check` sin problemas; `pip install --dry-run -r requirements-dev.txt` no instala ni actualiza nada.

## Etapa 2.3 – Defectos E-02 a E-07 (commit `6c63e99`)

Pruebas de regresión en `tests/test_correcciones.py`. Contra el código original fallaban 5 de 6 (E-07 pasaba porque `.gitignore` e índice ya estaban corregidos); con las correcciones pasan las 6.

| Pruebas | Ejecutadas | Aprobadas | Fallidas |
|---|---|---|---|
| Unitarias e integración | 29 | 29 | 0 |
| E2E headless (3 repeticiones) | 6 | 6 | 0 |

## Etapa 2.4 – Interfaz en español

Cambios:

- `todo_list/settings.py`: `LANGUAGE_CODE = 'es'`. Los mensajes de validación de Django (formularios de registro, login y campos obligatorios) se muestran en español con las traducciones incluidas en Django.
- `base/models.py`: `verbose_name` en español para los campos y el modelo (`título`, `descripción`, `completada`, `tarea`). Las etiquetas de los formularios generados se muestran en español.
- `base/migrations/0002_etiquetas_en_espanol.py`: migración generada por el cambio de `verbose_name`. `sqlmigrate base 0002` confirma que todas las operaciones son `(no-op)`: no altera el esquema ni los datos.
- Plantillas: `main.html` (`lang="es"`, título), `login.html`, `register.html`, `task_list.html`, `task.html`, `task_form.html`, `task_confirm_delete.html`. Se tradujeron textos visibles y botones; se reemplazó `<bold>` (etiqueta inexistente) por `<strong>`. Se conservaron `{% csrf_token %}`, `{{form.as_p}}`, nombres de campos y rutas.
- El contador usa `pluralize` en español: "1 tarea pendiente", "2 tareas pendientes".

Pruebas nuevas en `tests/test_idioma.py` (17 casos): `LANGUAGE_CODE`, `lang="es"`, ausencia de textos en inglés en las 7 páginas, etiquetas del formulario, lista vacía, plural del contador y mensajes de validación de registro, login y campo obligatorio. Antes de los cambios fallaban las 17.

| Pruebas | Ejecutadas | Aprobadas | Fallidas |
|---|---|---|---|
| Unitarias e integración (incluye 17 de idioma) | 46 | 46 | 0 |
| E2E headless (3 repeticiones) | 6 | 6 | 0 |
| E2E con ventana (1 repetición) | 2 | 2 | 0 |
| `manage.py check` | – | Sin problemas | – |
| `makemigrations --check` | – | Sin cambios pendientes | – |

## Etapa 5.1 – Modelo, migraciones y regla de eliminación

Cambios de requisitos: ver `docs/cambios_requisitos.md`.

Archivos:

- `base/models.py`: `created_by` (FK nullable, `SET_NULL`, `related_name='tareas_creadas'`); `user` pasa a `SET_NULL` con `related_name='tareas_asignadas'`.
- `base/migrations/0003_task_created_by.py`: `ALTER TABLE ADD COLUMN created_by_id` + índice. La parte de `user` es `(no-op)` en SQL.
- `base/migrations/0004_copiar_user_a_created_by.py`: `RunPython` que hace `UPDATE created_by = user` solo donde `created_by` es NULL. Reversa sin operación.
- `base/signals.py` + `base/apps.py`: regla de eliminación de usuarios (pre_delete guarda IDs vinculados; post_delete borra solo los que quedaron sin creador ni asignado; todo dentro de la transacción del borrado).
- `tests/conftest.py`: fixture `tarea_a` con `created_by=user_a` (C2).
- `scripts/verificar_db.py`: inspección de solo lectura de una base SQLite.

Verificación de SQL (`sqlmigrate`): `0002` todo `(no-op)`; `0003` solo `ADD COLUMN` + `CREATE INDEX`, sin reconstruir la tabla; `0004` Python.

Pruebas nuevas:

- `tests/test_eliminacion_usuarios.py` (13): `SET_NULL` en ambos campos, `related_name`, sin asignación implícita, tarea personal, creador eliminado con tarea asignada a otro, asignado eliminado, tarea sin asignado, tarea sin creador, tareas de otros intactas, huérfanas previas intactas, eliminación masiva, usuario sin tareas.
- `tests/test_migraciones.py` (4): columna agregada por 0003, copia de datos sin pérdida (títulos, descripciones, estado, fechas, `user`), no sobrescribe `created_by` existente, reversibilidad 0004 → 0002 sin pérdida.

Antes de implementar fallaban las 17.

| Pruebas | Ejecutadas | Aprobadas | Fallidas |
|---|---|---|---|
| Unitarias e integración | 63 | 63 | 0 |
| Orden alterado (migraciones primero) | 36 | 36 | 0 |
| E2E headless (3 repeticiones) | 6 | 6 | 0 |

### Migración de la base local

| Paso | Resultado |
|---|---|
| Copia `backups/db.sqlite3.20261109-pre-0003` | SHA-256 idéntico (`F030720E…CE92`), `integrity_check` ok, mismos conteos |
| Ensayo de `migrate` sobre copia temporal | 0002, 0003, 0004 OK; original sin cambios (mismo hash) |
| `migrate` real | 0002, 0003, 0004 OK |
| Estado posterior | `integrity_check` ok, `foreign_key_check` vacío, columna `created_by_id` presente, mismas filas en todas las tablas salvo `django_migrations` (19 → 22) |

Evidencias: `docs/evidencias/db_estado_pre_0003.json` y `docs/evidencias/db_estado_post_0004.json`.
La base local tiene 0 tareas, por lo que la copia de datos se verificó con las pruebas automáticas.

Reversión: `python manage.py migrate base 0002` o restaurar la copia de `backups/`.
