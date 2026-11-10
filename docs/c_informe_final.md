# c) Informe final del proceso de pruebas

> Sistema de Gestión de Tareas – Plásticos Sustentables · Autora: Jeraldin Caliz · Corte: 9 de noviembre de 2026 · Rama `feature/pruebas-qa` (commit `faa6169`)
>
> Documentos de la entrega: [a) Código fuente](a_codigo_fuente.md) · [b) Documentación de las pruebas](b_documentacion_pruebas.md) · [c) Informe final](c_informe_final.md)

Los identificadores de verificación (AUT-, TAR-, REG-, ELI-, MIG-, UI1-, UI2-, E2E-) corresponden a los casos de [b) Documentación de las pruebas](b_documentacion_pruebas.md#b2-casos-de-prueba).

## c.1 Resumen

El proyecto partió de un repositorio que no arrancaba: faltaba `base/urls.py` y 14 de 15 pruebas fallaban. El trabajo se organizó en fases (análisis, estabilización, funcionalidades, rediseño), con una línea base de pruebas antes de cada cambio, commits locales separados y documentación de cada defecto.

Resultado al cierre:

- 95 pruebas unitarias y de integración aprobadas y 16 E2E estables.
- 98 % de cobertura de sentencias en la aplicación `base`.
- 13 hallazgos registrados (tabla c.3): 12 corregidos y verificados (uno de ellos, E-11, en la herramienta de pruebas) y 1 abierto de severidad informativa (E-09).
- Interfaz en español y rediseño visual propio en login, registro y estructura general.

## c.2 Proceso

| Fase | Actividades | Commits |
|---|---|---|
| 1. Análisis | Inventario de apps, modelos, vistas, rutas, plantillas y pruebas; línea base; diagnóstico de defectos | – |
| 2. Estabilización | Restauración de rutas, recuperación de pruebas no descubiertas, esperas Selenium, dependencias de desarrollo, corrección de E-02 a E-07, interfaz en español | `6122a9f` … `edd5328` |
| 3. Funcionalidades | Etapa 5.1: `created_by`, `SET_NULL`, migración de datos con copia de seguridad, regla de eliminación de usuarios | `02def09` |
| 4. Rediseño | D-1 estructura general y D-2 autenticación, con recursos propios y pruebas de interfaz | `2b3a116`, `18bda6e` |

Procedimiento seguido para migrar la base local (etapa 5.1):

1. Copia de seguridad `backups/db.sqlite3.20261109-pre-0003` con SHA-256 idéntico al original.
2. `PRAGMA integrity_check` y conteo de filas en original y copia.
3. Ensayo de `migrate` sobre una copia temporal; el original no cambió.
4. `migrate` real y verificación posterior: integridad correcta, sin errores de claves foráneas, mismas filas en todas las tablas.

## c.3 Problemas encontrados y soluciones

| ID | Severidad | Problema | Causa | Solución | Verificación |
|---|---|---|---|---|---|
| E-00 | Alta | `IndentationError` en `test_acceptance.py` | Bloque de depuración con sangría de 1 espacio | Sangría corregida; el bloque se retiró después | `py_compile` sin errores |
| E-01 | Crítica | El proyecto no arrancaba | `base/urls.py` nunca se versionó | Rutas recuperadas del bytecode `urls.cpython-310.pyc` y versionadas | 8 rutas responden; 15/15 pruebas |
| H-01 | Media | 8 pruebas nunca se ejecutaban | Archivos `test.models.py` y `test.task.py` no cumplían `test_*.py`; a uno le faltaban imports | Renombrados con `git mv` e imports agregados, sin cambiar aserciones | 23/23 pruebas |
| E-02 | Media | El buscador perdía el texto buscado | Variable `seach_input` (errata) en la vista | Renombrada a `search_input` | REG-02 |
| E-03 | Media | Pendientes y completadas con el mismo icono | Ambas ramas usaban `task-complete-icon` | Pendiente usa `task-incomplete-icon` | REG-03 |
| E-04 | Baja | HTML inválido en la lista | Comillas duplicadas y `&#215` sin `;` | Marcado corregido | REG-04 |
| E-05 | Baja | El detalle no tenía estilos | `task.html` no extendía `main.html` | Agregado `{% extends %}` | REG-05 |
| E-06 | Baja | Selenium: `ElementNotInteractableException` | `<meta name="description">` coincidía con `By.NAME` antes que el `textarea` | Meta vacío eliminado; pruebas usan `By.ID` | REG-06, E2E-01 |
| E-07 | Baja | Base de datos versionada | `.gitignore` decía `.db.sqlite3` | Patrón corregido y `git rm --cached` con copia de seguridad | REG-07 |
| E-08 | Baja | CSS duplicado e interfaz en inglés | Estilos embebidos y `LANGUAGE_CODE='en-us'` | `LANGUAGE_CODE='es'`, textos traducidos; CSS movido a archivos estáticos (D-1) | UI1-02; las 17 pruebas de idioma se eliminaron en `4ee3c56` (ver c.4) |
| E-09 | Info | `SECRET_KEY` en el código y `DEBUG=True` | Configuración de desarrollo | **Abierto.** Para producción: variables de entorno y `DEBUG=False` | – |
| E-10 | Baja | Prueba E2E intermitente | `url_contains("/")` se cumplía con cualquier URL | `url_to_be` con la URL exacta y espera del elemento | 10/10 repeticiones |
| E-11 | Baja | Capturas "móviles" a 506 px en vez de 390 px | Chrome no admite ventanas tan angostas | Emulación con `Emulation.setDeviceMetricsOverride` y verificación de `innerWidth` | E2E-04, E2E-16/17 |

Ajustes e incidencias menores:

- Los errores de campo del registro heredaban la caja de los errores generales; se les aplicó un estilo propio.
- Cambios externos en `requirements*.txt` (herramientas de prueba mezcladas con producción y Selenium duplicado) se revirtieron con aprobación para mantener `requirements.txt` y `requirements-dev.txt` separados.
- `runserver` dejó de responder tras una recarga automática; se reinició. No afectó al código.

Cambio de requisitos documentado (etapa 5): `Task.user` dejó de ser a la vez dueño y creador. Ahora `created_by` es el creador y `user` el asignado, ambos con `SET_NULL`. La prueba existente `test_cascade_al_borrar_usuario` sigue pasando sin cambios gracias a la regla de eliminación de tareas huérfanas.

## c.4 Observaciones sobre el estado actual del repositorio

Los commits `4ee3c56`, `be9d473` y `faa6169` (posteriores a D-2) introdujeron estos cambios, que conviene revisar antes de la entrega:

| Cambio | Impacto | Recomendación |
|---|---|---|
| Se eliminó `tests/test_idioma.py` (17 pruebas) | La interfaz en español ya no tiene pruebas automáticas; la suite baja de 112 a 95 | Restaurarlo desde `edd5328` si se quiere conservar esa cobertura |
| Se eliminaron `docs/diagnostico_fase1.md`, `dependencias.md`, `cambios_requisitos.md`, `resultados_pruebas.md` y evidencias JSON | Se pierde la trazabilidad detallada por etapa | Los documentos a, b y c de esta entrega resumen su contenido; se pueden restaurar desde `02def09` o `18bda6e` |
| Se quitó la carpeta de Stitch de `.gitignore` | Hoy la carpeta no está en disco; si vuelve, podría versionarse por error | Volver a agregar la exclusión |
| Las capturas de `docs/evidencias/capturas/D-1/login_*` son las de D-2 | La evidencia de D-1 queda mezclada | Regenerar con `CAPTURAS=1 pytest tests/e2e/test_interfaz_d1_e2e.py::test_generar_capturas` |
| Se eliminó `.gitlab-ci.yml` | Solo queda GitHub Actions | Ninguna, si GitLab ya no se usa |
| El CI instala `pytest`, `pytest-django` y `selenium` sin versión | El CI puede usar versiones distintas a las locales | Usar `pip install -r requirements-dev.txt` |

## c.5 Trabajo pendiente

| Prioridad | Tarea | Requisito |
|---|---|---|
| Alta | Etapa 5.2: permisos de creador, asignado (solo cambia el estado) y administrador; ruta `task-status`; formulario con asignado; `TaskCreate` debe guardar `created_by` | 3 |
| Alta | Etapa 6: perfil (nombre, apellido, correo) y cambio de contraseña con vistas nativas de Django | 6, 7 |
| Media | Filtro por estado (todas, pendientes, completadas) | 4 |
| Media | Rediseño D-3 a D-5 (lista, formularios, detalle, confirmación, verificación final) | – |
| Baja | Prueba para GET a `/register/` con sesión (línea 36 de `views.py`) | – |
| Baja | E-09: configuración segura para producción | – |

## c.6 Conclusiones

- Las pruebas encontraron un defecto crítico (E-01) que impedía ejecutar el sistema y que no se veía en el entorno local por el bytecode en caché. Ejecutar la suite en un clon limpio (CI) lo habría detectado antes.
- La prueba E2E inestable (E-10) muestra que una espera mal formulada puede pasar casi siempre y ocultar errores; repetir las pruebas varias veces fue lo que permitió encontrarla.
- Escribir primero la prueba de regresión y confirmar que falla antes de corregir dio evidencia objetiva de cada corrección.
- La migración de datos se trató como una operación de riesgo: copia verificada, ensayo sobre una copia y verificación posterior. No hubo pérdida de datos.
- La autorización entre usuarios funciona para el modelo actual (cada usuario solo ve sus tareas), pero la asignación a otros usuarios necesita la etapa 5.2 antes de considerarse completa.
