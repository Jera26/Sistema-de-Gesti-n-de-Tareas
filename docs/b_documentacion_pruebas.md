# b) Documentación de las pruebas

> Sistema de Gestión de Tareas – Plásticos Sustentables · Autora: Jeraldin Caliz · Corte: 9 de noviembre de 2026 · Rama `feature/pruebas-qa` (commit `faa6169`)
>
> Documentos de la entrega: [a) Código fuente](a_codigo_fuente.md) · [b) Documentación de las pruebas](b_documentacion_pruebas.md) · [c) Informe final](c_informe_final.md)

| Dato | Valor |
|---|---|
| Entorno | Windows, Python 3.10.6, Django 4.1.5, SQLite |
| Herramientas de prueba | pytest 9.2.0, pytest-django 4.14.0, pytest-cov 7.1.0, Selenium 4.52.0, Chrome 156 |

## b.1 Estrategia

| Nivel | Objetivo | Herramienta | Ubicación |
|---|---|---|---|
| Unitarias | Modelo, validaciones, configuración de campos, migraciones | pytest + pytest-django | `test_models.py`, `test_migraciones.py`, `test_eliminacion_usuarios.py` |
| Integración | Vistas, rutas, plantillas, sesión, permisos y regresiones con el cliente de pruebas de Django | pytest-django (`client`) | `test_auth.py`, `test_tasks.py`, `test_task_extra.py`, `test_correcciones.py`, `test_interfaz_d1.py`, `test_interfaz_d2.py` |
| Aceptación (E2E) | Flujos completos en el navegador, responsive y accesibilidad | Selenium + Chrome, `live_server` | `tests/e2e/` |

Criterios aplicados durante todo el proceso:

- Cada defecto corregido tiene una prueba de regresión que falla con el código anterior y pasa con la corrección.
- No se modificaron aserciones para obtener resultados positivos.
- Las esperas de Selenium son condicionales (`url_to_be`, `presence_of_element_located`); no hay esperas fijas.
- Las pruebas E2E se repiten varias veces (con ventana y sin ventana) para detectar inestabilidad.

Datos de prueba (`tests/conftest.py`): usuarios `alice` y `bob` con contraseña `Pass12345!`, clientes con sesión iniciada (`client_a`, `client_b`) y la tarea `tarea_a` creada y asignada a alice.

## b.2 Casos de prueba

Inventario: 95 casos unitarios y de integración y 18 E2E (2 de ellos generan capturas y solo se ejecutan con `CAPTURAS=1`).

### Autenticación – `tests/test_auth.py` (6)

| ID | Caso | Resultado esperado |
|---|---|---|
| AUT-01 | Registro con datos válidos | 302 y usuario creado |
| AUT-02 | Registro con contraseñas distintas | 200 y usuario no creado |
| AUT-03 | Registro con usuario existente | 200 y un solo usuario |
| AUT-04 | Login correcto | 302 |
| AUT-05 | Login con contraseña incorrecta | 200 (permanece en login) |
| AUT-06 | Lista de tareas sin sesión | 302 a login |

### Modelo – `tests/test_models.py` (4)

| ID | Caso | Resultado esperado |
|---|---|---|
| MOD-01 | `str(tarea)` | Devuelve el título |
| MOD-02 | Estado por defecto | `complete` es `False` |
| MOD-03 | Título de 201 caracteres | `ValidationError` |
| MOD-04 | Título vacío | `ValidationError` |

### Tareas y autorización – `tests/test_tasks.py` (9) y `tests/test_task_extra.py` (4)

| ID | Caso | Resultado esperado |
|---|---|---|
| TAR-01 | Crear tarea | Queda asignada al usuario actual |
| TAR-02 | Lista con tareas de dos usuarios | Solo muestra las propias |
| TAR-03 | Búsqueda "resina" | Solo "Comprar resina" |
| TAR-04 | Eliminar tarea propia | La tarea deja de existir |
| TAR-05 | Eliminar al usuario dueño | Su tarea personal se elimina |
| TAR-06 | Bob abre el detalle de una tarea de Alice | 403 o 404 |
| TAR-07 | Bob intenta eliminar una tarea de Alice | La tarea sigue existiendo |
| TAR-08 | Bob intenta editar una tarea de Alice | El título no cambia |
| TAR-09 | Alice envía `user=bob` al editar | La tarea sigue asignada a Alice |
| TAR-10 | Editar tarea propia | Título y estado actualizados |
| TAR-11 | Contador con 2 pendientes y 1 completada | `count == 2` |
| TAR-12 | Crear tarea sin título | 200 y 0 tareas |
| TAR-13 | Cerrar sesión por POST | 302 |

### Regresión de defectos – `tests/test_correcciones.py` (6)

| ID | Defecto | Verificación |
|---|---|---|
| REG-02 | E-02 | El buscador conserva el texto (`search_input` y `value="resina"`) |
| REG-03 | E-03 | Pendiente usa `task-incomplete-icon` y completada `task-complete-icon` |
| REG-04 | E-04 | Sin comillas duplicadas en `href` ni `&#215` sin cerrar |
| REG-05 | E-05 | El detalle usa `base/main.html` |
| REG-06 | E-06 | Un único `name="description"` en el formulario |
| REG-07 | E-07 | `db.sqlite3` ignorada y no versionada |

### Eliminación de usuarios – `tests/test_eliminacion_usuarios.py` (13)

| ID | Caso | Resultado esperado |
|---|---|---|
| ELI-01 | Configuración de `created_by` y `user` | Ambos `SET_NULL` |
| ELI-02 | Opcionalidad | Ambos `null` y `blank` |
| ELI-03 | `related_name` | `tareas_creadas` y `tareas_asignadas` funcionan |
| ELI-04 | Crear con `user` sin `created_by` | `created_by` queda vacío (sin deducción implícita) |
| ELI-05 | Eliminar dueño de tarea personal | La tarea se elimina |
| ELI-06 | Eliminar creador de tarea asignada a otro | Se conserva; `created_by` vacío |
| ELI-07 | Eliminar asignado | Se conserva; `user` vacío |
| ELI-08 | Eliminar creador de tarea sin asignado | La tarea se elimina |
| ELI-09 | Eliminar asignado de tarea sin creador | La tarea se elimina |
| ELI-10 | Tareas de otros usuarios | No se modifican |
| ELI-11 | Tarea huérfana previa no vinculada | No se elimina |
| ELI-12 | Borrado masivo de creador y asignado | Se elimina solo la que queda huérfana |
| ELI-13 | Usuario sin tareas | No se elimina nada |

### Migraciones – `tests/test_migraciones.py` (4)

| ID | Caso | Resultado esperado |
|---|---|---|
| MIG-01 | Aplicar 0003 | Aparece la columna `created_by_id` |
| MIG-02 | Aplicar 0004 sobre 4 filas creadas con el esquema 0002 | `created_by = user`; título, descripción, estado, fecha y `user` intactos |
| MIG-03 | 0004 con `created_by` ya definido | No se sobrescribe |
| MIG-04 | Revertir 0004 → 0002 | Columna eliminada y datos intactos |

### Interfaz D-1 – `tests/test_interfaz_d1.py` (28)

| ID | Caso | Casos |
|---|---|---|
| UI1-01 | Los 5 recursos estáticos existen | 5 |
| UI1-02 | Las 7 páginas no cargan recursos externos, ni Stitch, y sí los CSS/JS locales | 7 |
| UI1-03 | Barra lateral y superior visibles con sesión | 1 |
| UI1-04 | Sin barra lateral en login y registro | 1 |
| UI1-05 | "Mis tareas" marcada como activa en lista, detalle, edición y borrado | 4 |
| UI1-06 | "Nueva tarea" marcada como activa | 1 |
| UI1-07 | Cierre de sesión es un formulario POST con CSRF | 1 |
| UI1-08 | No quedan enlaces GET de cierre de sesión | 1 |
| UI1-09 | Cerrar sesión termina la sesión | 1 |
| UI1-10 | Barra superior muestra el usuario real | 1 |
| UI1-11 | Nombre completo y rol "Administrador" para `is_staff` | 1 |
| UI1-12 | Enlace de administración oculto para usuarios normales | 1 |
| UI1-13 | Título de sección en `<title>` y ruta de navegación | 1 |
| UI1-14 | Enlace "Saltar al contenido", menú con `aria-*`, iconos ocultos a lectores de pantalla | 1 |
| UI1-15 | Formulario de edición conserva CSRF y campos | 1 |

### Interfaz D-2 – `tests/test_interfaz_d2.py` (21)

| ID | Caso | Casos |
|---|---|---|
| UI2-01 | Login y registro usan la tarjeta nueva y no el diseño anterior | 2 |
| UI2-02 | Cada campo tiene `<label for>` asociado | 2 |
| UI2-03 | Se conservan `name`, CSRF y método POST | 2 |
| UI2-04 | Se conserva el autocompletado de Django | 1 |
| UI2-05 | Campos obligatorios marcados | 2 |
| UI2-06 | Un botón de mostrar contraseña por cada campo de contraseña | 2 |
| UI2-07 | Ayuda de Django visible en el registro | 1 |
| UI2-08 | Error de contraseñas distintas junto al campo | 1 |
| UI2-09 | Error de usuario duplicado junto al campo | 1 |
| UI2-10 | Error general de login en `ul.errorlist` | 1 |
| UI2-11 | El usuario escrito se conserva tras el error | 1 |
| UI2-12 | Enlaces cruzados login ↔ registro | 1 |
| UI2-13 | No aparecen funciones inexistentes (recordarme, recuperar contraseña…) | 2 |
| UI2-14 | El panel describe solo funciones reales | 1 |
| UI2-15 | Registro, cierre y login siguen funcionando | 1 |

### Aceptación E2E – `tests/e2e/` (18)

| ID | Caso | Archivo |
|---|---|---|
| E2E-01 | Flujo completo: registro → crear tarea → verla en la lista | `test_acceptance.py` |
| E2E-02 | Login incorrecto muestra el error | `test_acceptance.py` |
| E2E-03 | Estilos locales cargados (color de fondo) | `test_interfaz_d1_e2e.py` |
| E2E-04 | Sin desbordamiento horizontal en lista y nueva tarea (1440/834/390 px) | `test_interfaz_d1_e2e.py` |
| E2E-05 | Menú móvil: abrir, cerrar con Escape y con el fondo, foco devuelto | `test_interfaz_d1_e2e.py` |
| E2E-06 | Barra lateral fija en escritorio | `test_interfaz_d1_e2e.py` |
| E2E-07 | "Saltar al contenido" con teclado | `test_interfaz_d1_e2e.py` |
| E2E-08 | Cerrar sesión desde la barra lateral | `test_interfaz_d1_e2e.py` |
| E2E-09 | Capturas D-1 (solo `CAPTURAS=1`) | `test_interfaz_d1_e2e.py` |
| E2E-10/11 | Mostrar y ocultar contraseña en login y registro | `test_interfaz_d2_e2e.py` |
| E2E-12 | Errores asociados al campo (`aria-invalid`, `aria-describedby`) | `test_interfaz_d2_e2e.py` |
| E2E-13 | Ayuda asociada al campo | `test_interfaz_d2_e2e.py` |
| E2E-14/15 | Panel informativo visible solo en escritorio | `test_interfaz_d2_e2e.py` |
| E2E-16/17 | Sin desbordamiento horizontal en login y registro | `test_interfaz_d2_e2e.py` |
| E2E-18 | Capturas D-2 (solo `CAPTURAS=1`) | `test_interfaz_d2_e2e.py` |

## b.3 Resultados

### Evolución de la suite

| Momento | Unitarias + integración | E2E | Observación |
|---|---|---|---|
| Línea base inicial | 1 / 15 aprobadas | No ejecutables | Faltaba `base/urls.py` (E-01) |
| Tras restaurar rutas | 15 / 15 | 1 / 2 | Falla intermitente E2E (E-06, E-10) |
| Tras recuperar archivos no descubiertos | 23 / 23 | 2 / 2 intermitente | +8 pruebas |
| Tras E-02 a E-07 | 29 / 29 | 2 / 2 estables | +6 regresiones |
| Etapa 4 (español) | 46 / 46 | 2 / 2 | +17 pruebas de idioma |
| Etapa 5.1 (modelo) | 63 / 63 | 2 / 2 | +17 eliminación y migraciones |
| D-1 | 91 / 91 | 8 / 8 | +28 integración, +6 E2E |
| D-2 | 112 / 112 | 16 / 16 (+2 omitidas) | +21 integración, +8 E2E |
| **Estado actual (`faa6169`)** | **95 / 95** | **16 / 16 (+2 omitidas)** | `tests/test_idioma.py` (17) fue eliminado en el commit `4ee3c56` (ver [informe final, c.4](c_informe_final.md#c4-observaciones-sobre-el-estado-actual-del-repositorio)) |

### Ejecución actual

| Suite | Comando | Ejecutadas | Aprobadas | Fallidas | Omitidas |
|---|---|---|---|---|---|
| Unitarias e integración | `pytest --ignore=tests/e2e` | 95 | 95 | 0 | 0 |
| E2E headless (3 repeticiones, D-2) | `E2E_HEADLESS=1 pytest tests/e2e` | 48 | 48 | 0 | 6 |
| E2E con ventana (1 repetición, D-2) | `pytest tests/e2e` | 16 | 16 | 0 | 2 |

Las omitidas son los 2 generadores de capturas, que solo se ejecutan con `CAPTURAS=1`.

### Estabilidad E2E

| Momento | Repeticiones | Resultado |
|---|---|---|
| Antes de E-10 | 5 | 4 aprobadas, 1 fallo intermitente |
| Después de E-10 | 10 (5 con ventana, 5 headless) | 10 / 10 |
| D-1 | 4 | 4 / 4 |
| D-2 | 4 | 4 / 4 |

## b.4 Análisis de cobertura

Comando: `pytest --ignore=tests/e2e --cov=base --cov-branch --cov-report=term-missing`

| Módulo | Sentencias | Sin cubrir | Ramas | Ramas parciales | Cobertura |
|---|---|---|---|---|---|
| `base/admin.py` | 3 | 0 | 0 | 0 | 100 % |
| `base/apps.py` | 6 | 0 | 0 | 0 | 100 % |
| `base/models.py` | 15 | 0 | 0 | 0 | 100 % |
| `base/signals.py` | 15 | 0 | 2 | 0 | 100 % |
| `base/urls.py` | 4 | 0 | 0 | 0 | 100 % |
| `base/views.py` | 67 | 1 | 6 | 2 | 96 % |
| `base/migrations/*` | 27 | 0 | 0 | 0 | 100 % |
| **Total** | **137** | **1** | **8** | **2** | **98 %** |

Líneas y ramas sin cubrir en `base/views.py`:

| Ubicación | Código | Motivo | Acción recomendada |
|---|---|---|---|
| Línea 36 | `return redirect('tasks')` en `RegisterPage.get` | Ninguna prueba abre `/register/` con sesión iniciada | Agregar una prueba: GET a `register` con `client_a` → 302 a `tasks` |
| Rama 30→32 | `if user is not None` falso en `RegisterPage.form_valid` | `UserCreationForm.save()` siempre devuelve un usuario; la rama es inalcanzable | Ninguna (código defensivo) |

Limitaciones de la medición:

- `coverage.py` mide solo Python. Las plantillas, el CSS y el JavaScript se verifican con las pruebas de integración (HTML generado) y las E2E (comportamiento en Chrome).
- Un 98 % de líneas no garantiza que todos los escenarios estén probados: la autorización entre creador y asignado no se puede probar todavía porque las vistas de la etapa 5.2 no existen.
- Las migraciones aparecen al 100 % porque se importan; su comportamiento real lo verifican las 4 pruebas de `test_migraciones.py`.

## Anexo: cómo reproducir los resultados

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements-dev.txt
python manage.py migrate

# Unitarias e integración
pytest -q --ignore=tests/e2e

# Cobertura (sentencias y ramas)
pytest --ignore=tests/e2e --cov=base --cov-branch --cov-report=term-missing

# Aceptación con Selenium (requiere Chrome)
pytest tests/e2e
$env:E2E_HEADLESS="1"; pytest tests/e2e      # sin ventana

# Capturas de evidencia
$env:CAPTURAS="1"; $env:E2E_HEADLESS="1"; pytest tests/e2e -k generar_capturas

# Ejecutar la aplicación
python manage.py runserver
```

Usuario de prueba en la base local: `alice` / `Pass12345!`.
