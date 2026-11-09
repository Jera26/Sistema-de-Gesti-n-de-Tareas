# Diagnóstico – Fase 1 (Análisis)

Fecha: 9 de noviembre de 2026
Rama: `feature/pruebas-qa` (commit base `9f49514`)
Entorno: Python 3.10.6, Django 4.1.5, SQLite

Este documento conserva el estado del proyecto **antes** de cualquier modificación.

## 1. Bloqueo crítico

`todo_list/urls.py` incluye `base.urls`, pero `base/urls.py` no existía en disco ni estaba versionado en Git
(solo existía `base/__pycache__/urls.cpython-*.pyc`). `python manage.py check` fallaba con
`ModuleNotFoundError: No module named 'base.urls'`.

Rutas recuperadas desde el bytecode `base/__pycache__/urls.cpython-310.pyc`:

| Ruta | Vista | Nombre |
|---|---|---|
| `login/` | `CustomLoginView` | `login` |
| `logout/` | `LogoutView(next_page='login')` | `logout` |
| `register/` | `RegisterPage` | `register` |
| `''` | `TaskList` | `tasks` |
| `task/<int:pk>` | `TaskDetail` | `task` |
| `create-task/` | `TaskCreate` | `task-create` |
| `update-task/<int:pk>/` | `TaskUpdate` | `task-update` |
| `delete-task/<int:pk>/` | `TaskDelete` | `task-delete` |

## 2. Estructura

- Una app Django: `base`.
- Modelo `Task`: `user` (FK nullable, CASCADE), `title` (200), `description`, `complete`, `created`. Una migración (`0001_initial`).
- Sin `forms.py`: los formularios se generan con `fields=[...]` en vistas genéricas; registro con `UserCreationForm`.
- 7 plantillas en `base/templates/base/`; todo el CSS inline en `main.html`.
- Sin carpeta `static/` ni `STATICFILES_DIRS`.
- CI: GitHub Actions (Python 3.11) y GitLab CI (Python 3.10).

## 3. Requisitos funcionales

| # | Requisito | Estado |
|---|---|---|
| 1 | Registro e inicio de sesión | Implementado |
| 2 | Crear, editar y eliminar tareas | Implementado (detalle `task.html` mínimo y sin enlace) |
| 3 | Asignación a usuarios | No implementado |
| 4 | Filtrado y búsqueda | Parcial (solo búsqueda por título) |
| 5 | Ver pendientes y completadas | Parcial (con defecto de icono) |
| 6 | Gestión de perfiles | No implementado |
| 7 | Editar perfil y cambiar contraseña | No implementado |

## 4. Pruebas existentes (línea base sin `base/urls.py`)

Comando: `pytest -q --ignore=tests/e2e`
Resultado: **14 fallidas, 1 aprobada** (todas por `ModuleNotFoundError: base.urls`).

- `tests/test.models.py` y `tests/test.task.py` no son descubiertas por pytest (`python_files = test_*.py`).
- `tests/test.task.py` carece de imports (`reverse`, `Task`) y de `pytestmark = pytest.mark.django_db`.
- Pruebas E2E con Selenium requieren Chrome con interfaz (headless comentado).
- `requirements.txt` no incluye pytest, pytest-django ni selenium.

## 5. Defectos identificados

| ID | Severidad | Defecto |
|---|---|---|
| E-01 | Crítica | `base/urls.py` ausente y no versionado |
| E-02 | Media | Vista envía `seach_input`; la plantilla usa `search_input` (el buscador pierde el texto) |
| E-03 | Media | Tareas pendientes y completadas usan el mismo icono `task-complete-icon` |
| E-04 | Baja | HTML inválido en `task_list.html` (`""`, `&#215` sin `;`) |
| E-05 | Baja | `task.html` no extiende `main.html` |
| E-06 | Baja | `<meta name="description">` colisiona con el campo `description` al buscar por `By.NAME` |
| E-07 | Baja | `.gitignore` contiene `.db.sqlite3` en vez de `db.sqlite3` |
| E-08 | Baja | CSS duplicado e interfaz en inglés (`LANGUAGE_CODE='en-us'`) |
| E-09 | Info | `SECRET_KEY` en código y `DEBUG=True` |
