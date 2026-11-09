# Estructura de dependencias

Las dependencias de producción y las de desarrollo/pruebas están separadas.

| Archivo | Uso | Instalación |
|---|---|---|
| `requirements.txt` | Dependencias necesarias para ejecutar la aplicación | `pip install -r requirements.txt` |
| `requirements-dev.txt` | Herramientas de pruebas; incluye `requirements.txt` con `-r` | `pip install -r requirements-dev.txt` |

## `requirements.txt` (producción)

| Paquete | Versión |
|---|---|
| asgiref | 3.6.0 |
| backports.zoneinfo | 0.2.1 (solo Python < 3.9) |
| Django | 4.1.5 |
| djangorestframework | 3.14.0 |
| pytz | 2022.7.1 |
| sqlparse | 0.4.3 |
| tzdata | 2022.7 |

## `requirements-dev.txt` (desarrollo y pruebas)

Versiones fijadas a las instaladas en el entorno virtual (Python 3.10.6), verificadas el 9/11/2026.

| Paquete | Versión | Uso |
|---|---|---|
| pytest | 9.2.0 | Ejecutor de pruebas |
| pytest-django | 4.14.0 | Integración de pytest con Django (`db`, `client`, `live_server`) |
| pytest-cov | 7.1.0 | Cobertura de código (`--cov=base`) |
| selenium | 4.52.0 | Pruebas E2E en Chrome |

Las dependencias transitivas (por ejemplo `trio`, `urllib3`, `coverage`) no se fijan; las resuelve pip a partir de los paquetes anteriores.

## Verificación

| Comando | Resultado |
|---|---|
| `pip check` | `No broken requirements found.` |
| `pip install --dry-run -r requirements-dev.txt` | Todo satisfecho; no instala ni actualiza paquetes |
| Selenium en `requirements.txt` | 0 apariciones |
| Selenium en `requirements-dev.txt` | 1 aparición |
| Salto de línea final | Presente en ambos archivos |

## Incidente del 9/11/2026

Durante la etapa 3 aparecieron cambios externos (no hechos por el asistente):

- `requirements-dev.txt` fue eliminado del disco.
- En `requirements.txt` se agregaron `pytest`, `pytest-django`, `pytest-cov` y `selenium` (este último dos veces), sin salto de línea final.

El diff completo se conserva en `docs/evidencias/diff_externo_requirements_20261109.txt`. El diff contenía únicamente líneas de herramientas de prueba y líneas en blanco; no había otros cambios que conservar.

Corrección (aprobada, opción 1):

1. `requirements-dev.txt` restaurado desde el commit `75352b0` (hash de contenido idéntico, `41a1ac1`).
2. `requirements.txt` restaurado a su versión versionada, retirando solo las herramientas de prueba.

## Pendiente (no aplicado)

Los pipelines de CI (`.github/workflows/tests.yml` y `.gitlab-ci.yml`) instalan `pytest` y `pytest-django` sin versión fija. Podrían usar `pip install -r requirements-dev.txt` para usar las mismas versiones que el entorno local. No se modificaron porque no fue solicitado.
