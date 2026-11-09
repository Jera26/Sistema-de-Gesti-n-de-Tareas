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
