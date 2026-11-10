# Sistema de Gestión de Tareas: pruebas QA

Aplicación web para crear, editar y eliminar tareas de los empleados de **Plásticos Sustentables**, con registro, inicio de sesión y gestión de tareas propias. Este repositorio es  un proyecto Django agrega un plan de pruebas manuales y automatizadas.


## Tecnologías

Python 3.10+, Django 4.1, Django REST Framework, SQLite, pytest, pytest-django, pytest-cov y Selenium WebDriver.

## Instalación

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

La aplicación queda en `http://127.0.0.1:8000/`.

## Ejecutar las pruebas

| Qué | Comando |
|---|---|
| Unitarias e integración | `pytest -q --ignore=tests/e2e` |
| Con cobertura | `pytest --ignore=tests/e2e --cov=base --cov-report=html` |
| Aceptación (Selenium, requiere Chrome) | `pytest tests/e2e` |
| Aceptación sin ventana | `$env:E2E_HEADLESS=1; pytest tests/e2e` |


## Estructura

```
base/           Aplicación (modelos, vistas, plantillas)
todo_list/      Configuración del proyecto Django
tests/          Pruebas unitarias, de integración y de seguridad
tests/e2e/      Pruebas de aceptación con Selenium
scripts/        Utilidades (inspección de la base de datos)
```

## Integración continua

GitHub Actions ejecuta las pruebas en cada push y Pull Request (`.github/workflows/tests.yml`).

## Autor

Jeraldin Caliz 