# Sistema de Gestión de Tareas – Plásticos Sustentables

## Entrega final: código fuente, documentación de pruebas e informe de QA

| Dato | Valor |
|---|---|
| Autora | Jeraldin Caliz |
| Fecha de corte | 9 de noviembre de 2026 |
| Rama | `feature/pruebas-qa` |
| Último commit revisado | `faa6169` |
| Entorno | Windows, Python 3.10.6, Django 4.1.5, SQLite |
| Herramientas de prueba | pytest 9.2.0, pytest-django 4.14.0, pytest-cov 7.1.0, Selenium 4.52.0, Chrome 156 |

Contenido:

- [a) Código fuente](#a-código-fuente-del-sistema)
- [b) Documentación de las pruebas](#b-documentación-de-las-pruebas)
- [c) Informe final](#c-informe-final-del-proceso-de-pruebas)
- [Anexo: cómo reproducir los resultados](#anexo-cómo-reproducir-los-resultados)

---

## a) Código fuente del sistema

### a.1 Descripción

Aplicación web Django para que los empleados de Plásticos Sustentables registren y gestionen tareas. Permite registrarse, iniciar y cerrar sesión, crear, ver, editar, eliminar y buscar tareas, y distinguir las tareas pendientes de las completadas. Cada usuario solo accede a sus propias tareas.

El código fuente completo está en el repositorio Git. Esta sección describe su organización e incluye los archivos principales del backend.

### a.2 Estructura del proyecto

```text
django-todo/
├── manage.py
├── requirements.txt            Dependencias de la aplicación
├── requirements-dev.txt        Herramientas de prueba (incluye requirements.txt)
├── pytest.ini                  Configuración de pytest (DJANGO_SETTINGS_MODULE, test_*.py)
├── Readme.MD
├── .github/workflows/tests.yml Integración continua (unitarias + E2E)
├── todo_list/                  Proyecto Django
│   ├── settings.py             LANGUAGE_CODE='es', SQLite, LOGIN_URL='login'
│   └── urls.py                 admin/ + include('base.urls')
├── base/                       Aplicación principal
│   ├── models.py               Modelo Task
│   ├── views.py                Vistas basadas en clases
│   ├── urls.py                 8 rutas
│   ├── signals.py              Regla de eliminación de usuarios
│   ├── apps.py                 Registra las señales
│   ├── admin.py
│   ├── migrations/             0001 a 0004
│   ├── templates/base/         7 plantillas + 7 parciales
│   └── static/base/            CSS, JS, logo e iconos propios
├── tests/                      Pruebas unitarias y de integración
│   ├── conftest.py             Fixtures compartidas
│   └── e2e/                    Pruebas de aceptación con Selenium
├── scripts/verificar_db.py     Inspección de solo lectura de la base SQLite
└── docs/                       Documentación y evidencias
```

Tamaño del código (líneas, sin migraciones):

| Componente | Archivos | Líneas |
|---|---|---|
| Backend Python (`base/*.py`, `todo_list/*.py`) | 12 | 364 |
| Plantillas Django | 14 | 306 |
| CSS, JS, SVG | 5 | 777 |
| Pruebas (`tests/`) | 13 | 1.038 |

### a.3 Modelo de datos

`Task` (tabla `base_task`):

| Campo | Tipo | Descripción |
|---|---|---|
| `user` | FK → `User`, nullable, `SET_NULL` | Usuario asignado (`related_name='tareas_asignadas'`) |
| `created_by` | FK → `User`, nullable, `SET_NULL` | Usuario creador (`related_name='tareas_creadas'`) |
| `title` | `CharField(200)` | Título, obligatorio |
| `description` | `TextField`, opcional | Descripción |
| `complete` | `BooleanField`, por defecto `False` | Estado: Pendiente / Completada |
| `created` | `DateTimeField(auto_now_add)` | Fecha de creación |

`base/models.py`:

```python
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Task(models.Model):
    # Usuario asignado a la tarea.
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tareas_asignadas', verbose_name='asignada a')
    # Usuario que creó la tarea.
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tareas_creadas', verbose_name='creada por')
    title = models.CharField('título', max_length=200)
    description = models.TextField('descripción', null=True, blank=True)
    complete = models.BooleanField('completada', default=False)
    created = models.DateTimeField('creada', auto_now_add=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['complete']
        verbose_name = 'tarea'
        verbose_name_plural = 'tareas'
```

Migraciones:

| Migración | Operación | SQL real (`sqlmigrate`) |
|---|---|---|
| `0001_initial` | Crea `Task` | `CREATE TABLE` |
| `0002_etiquetas_en_espanol` | `verbose_name` en español | Todo `(no-op)` |
| `0003_task_created_by` | Agrega `created_by`; `user` pasa a `SET_NULL` | `ALTER TABLE ADD COLUMN` + índice; la parte de `user` es `(no-op)` |
| `0004_copiar_user_a_created_by` | Copia `user` → `created_by` donde está vacío | Un `UPDATE`; reversa sin operación |

### a.4 Rutas (`base/urls.py`)

```python
from django.urls import path
from .views import TaskList, TaskDetail, TaskCreate, TaskUpdate, TaskDelete, CustomLoginView, RegisterPage
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegisterPage.as_view(), name='register'),
    path('', TaskList.as_view(), name='tasks'),
    path('task/<int:pk>', TaskDetail.as_view(), name='task'),
    path('create-task/', TaskCreate.as_view(), name='task-create'),
    path('update-task/<int:pk>/', TaskUpdate.as_view(), name='task-update'),
    path('delete-task/<int:pk>/', TaskDelete.as_view(), name='task-delete'),
]
```

### a.5 Vistas (`base/views.py`)

```python
class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self) -> str:
        return reverse_lazy('tasks')

class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args,**kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(title__icontains=search_input)

        context['search_input'] = search_input
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
```

Control de acceso: todas las vistas de tareas usan `LoginRequiredMixin` y filtran por `user=request.user`. Una tarea de otro usuario responde 404, incluso si se cambia el ID en la URL.

### a.6 Regla de eliminación de usuarios (`base/signals.py`)

```python
@receiver(pre_delete, sender=User, dispatch_uid='base_tareas_vinculadas_pre_delete')
def guardar_tareas_vinculadas(sender, instance, **kwargs):
    ids = Task.objects.filter(
        Q(created_by=instance) | Q(user=instance)
    ).values_list('pk', flat=True)
    setattr(instance, _ATRIBUTO, list(ids))


@receiver(post_delete, sender=User, dispatch_uid='base_tareas_huerfanas_post_delete')
def eliminar_tareas_huerfanas(sender, instance, **kwargs):
    ids = getattr(instance, _ATRIBUTO, None)
    if ids:
        Task.objects.filter(
            pk__in=ids, created_by__isnull=True, user__isnull=True
        ).delete()
```

Al eliminar un usuario se conservan las tareas que todavía tienen otro usuario vinculado y se borran solo las que quedarían sin creador ni asignado. Todo ocurre dentro de la transacción del borrado.

### a.7 Interfaz

Diseño propio inspirado en las referencias de Google Stitch. No se incorporó ningún archivo de Stitch: las plantillas, estilos, iconos y logo son del proyecto y no dependen de CDN.

| Archivo | Contenido |
|---|---|
| `static/base/css/tokens.css` | Variables: azul `#0051d5`, fondo `#f9f9ff`, marino `#172554`, tipografía Inter con respaldo del sistema, espaciado, radios, sombras |
| `static/base/css/app.css` | Base, accesibilidad, barra lateral, barra superior, componentes, autenticación y responsive |
| `static/base/js/app.js` | Menú móvil, mostrar/ocultar contraseña, `aria-describedby` en campos. La aplicación funciona sin JavaScript |
| `templates/base/main.html` | Estructura general: barra lateral y superior con sesión; tarjeta centrada sin sesión |
| `templates/base/partials/` | `_sidebar`, `_topbar`, `_form_field`, `_auth_panel`, `_auth_brand`, `_icon`, `_page_title` |

Estado del rediseño:

| Etapa | Plantillas | Estado |
|---|---|---|
| D-1 | `main.html`, barra lateral, barra superior | Terminada (`2b3a116`) |
| D-2 | `login.html`, `register.html` | Terminada (`18bda6e`) |
| D-3 | `task_list.html` | Pendiente (usa estilos de compatibilidad con la paleta nueva) |
| D-4 | `task_form.html`, `task.html`, `task_confirm_delete.html` | Pendiente (ídem) |
| D-5 | Verificación final responsive y accesibilidad | Pendiente |

### a.8 Cobertura de los requisitos funcionales

| # | Requisito | Estado |
|---|---|---|
| 1 | Registro e inicio de sesión | Implementado y probado |
| 2 | Crear, editar y eliminar tareas | Implementado y probado |
| 3 | Asignación de tareas a usuarios | Parcial: modelo y migración listos (etapa 5.1); faltan vistas y permisos (etapa 5.2) |
| 4 | Filtrado y búsqueda | Parcial: búsqueda por título; falta filtro por estado |
| 5 | Ver pendientes y completadas | Implementado: indicador de estado y contador de pendientes |
| 6 | Gestión de perfiles | No implementado (etapa 6) |
| 7 | Editar perfil y cambiar contraseña | No implementado (etapa 6) |

---

## b) Documentación de las pruebas

### b.1 Estrategia

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

### b.2 Casos de prueba

Inventario: 95 casos unitarios y de integración y 18 E2E (2 de ellos generan capturas y solo se ejecutan con `CAPTURAS=1`).

#### Autenticación – `tests/test_auth.py` (6)

| ID | Caso | Resultado esperado |
|---|---|---|
| AUT-01 | Registro con datos válidos | 302 y usuario creado |
| AUT-02 | Registro con contraseñas distintas | 200 y usuario no creado |
| AUT-03 | Registro con usuario existente | 200 y un solo usuario |
| AUT-04 | Login correcto | 302 |
| AUT-05 | Login con contraseña incorrecta | 200 (permanece en login) |
| AUT-06 | Lista de tareas sin sesión | 302 a login |

#### Modelo – `tests/test_models.py` (4)

| ID | Caso | Resultado esperado |
|---|---|---|
| MOD-01 | `str(tarea)` | Devuelve el título |
| MOD-02 | Estado por defecto | `complete` es `False` |
| MOD-03 | Título de 201 caracteres | `ValidationError` |
| MOD-04 | Título vacío | `ValidationError` |

#### Tareas y autorización – `tests/test_tasks.py` (9) y `tests/test_task_extra.py` (4)

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

#### Regresión de defectos – `tests/test_correcciones.py` (6)

| ID | Defecto | Verificación |
|---|---|---|
| REG-02 | E-02 | El buscador conserva el texto (`search_input` y `value="resina"`) |
| REG-03 | E-03 | Pendiente usa `task-incomplete-icon` y completada `task-complete-icon` |
| REG-04 | E-04 | Sin comillas duplicadas en `href` ni `&#215` sin cerrar |
| REG-05 | E-05 | El detalle usa `base/main.html` |
| REG-06 | E-06 | Un único `name="description"` en el formulario |
| REG-07 | E-07 | `db.sqlite3` ignorada y no versionada |

#### Eliminación de usuarios – `tests/test_eliminacion_usuarios.py` (13)

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

#### Migraciones – `tests/test_migraciones.py` (4)

| ID | Caso | Resultado esperado |
|---|---|---|
| MIG-01 | Aplicar 0003 | Aparece la columna `created_by_id` |
| MIG-02 | Aplicar 0004 sobre 4 filas creadas con el esquema 0002 | `created_by = user`; título, descripción, estado, fecha y `user` intactos |
| MIG-03 | 0004 con `created_by` ya definido | No se sobrescribe |
| MIG-04 | Revertir 0004 → 0002 | Columna eliminada y datos intactos |

#### Interfaz D-1 – `tests/test_interfaz_d1.py` (28)

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

#### Interfaz D-2 – `tests/test_interfaz_d2.py` (21)

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

#### Aceptación E2E – `tests/e2e/` (18)

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

### b.3 Resultados

#### Evolución de la suite

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
| **Estado actual (`faa6169`)** | **95 / 95** | **16 / 16 (+2 omitidas)** | `tests/test_idioma.py` (17) fue eliminado en el commit `4ee3c56` (ver c.4) |

#### Ejecución actual

| Suite | Comando | Ejecutadas | Aprobadas | Fallidas | Omitidas |
|---|---|---|---|---|---|
| Unitarias e integración | `pytest --ignore=tests/e2e` | 95 | 95 | 0 | 0 |
| E2E headless (3 repeticiones, D-2) | `E2E_HEADLESS=1 pytest tests/e2e` | 48 | 48 | 0 | 6 |
| E2E con ventana (1 repetición, D-2) | `pytest tests/e2e` | 16 | 16 | 0 | 2 |

Las omitidas son los 2 generadores de capturas, que solo se ejecutan con `CAPTURAS=1`.

#### Estabilidad E2E

| Momento | Repeticiones | Resultado |
|---|---|---|
| Antes de E-10 | 5 | 4 aprobadas, 1 fallo intermitente |
| Después de E-10 | 10 (5 con ventana, 5 headless) | 10 / 10 |
| D-1 | 4 | 4 / 4 |
| D-2 | 4 | 4 / 4 |

### b.4 Análisis de cobertura

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

---

## c) Informe final del proceso de pruebas

### c.1 Resumen

El proyecto partió de un repositorio que no arrancaba: faltaba `base/urls.py` y 14 de 15 pruebas fallaban. El trabajo se organizó en fases (análisis, estabilización, funcionalidades, rediseño), con una línea base de pruebas antes de cada cambio, commits locales separados y documentación de cada defecto.

Resultado al cierre:

- 95 pruebas unitarias y de integración aprobadas y 16 E2E estables.
- 98 % de cobertura de sentencias en la aplicación `base`.
- 13 hallazgos registrados (tabla c.3): 12 corregidos y verificados (uno de ellos, E-11, en la herramienta de pruebas) y 1 abierto de severidad informativa (E-09).
- Interfaz en español y rediseño visual propio en login, registro y estructura general.

### c.2 Proceso

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

### c.3 Problemas encontrados y soluciones

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

### c.4 Observaciones sobre el estado actual del repositorio

Los commits `4ee3c56`, `be9d473` y `faa6169` (posteriores a D-2) introdujeron estos cambios, que conviene revisar antes de la entrega:

| Cambio | Impacto | Recomendación |
|---|---|---|
| Se eliminó `tests/test_idioma.py` (17 pruebas) | La interfaz en español ya no tiene pruebas automáticas; la suite baja de 112 a 95 | Restaurarlo desde `edd5328` si se quiere conservar esa cobertura |
| Se eliminaron `docs/diagnostico_fase1.md`, `dependencias.md`, `cambios_requisitos.md`, `resultados_pruebas.md` y evidencias JSON | Se pierde la trazabilidad detallada por etapa | Este documento resume su contenido; se pueden restaurar desde `02def09` o `18bda6e` |
| Se quitó la carpeta de Stitch de `.gitignore` | Hoy la carpeta no está en disco; si vuelve, podría versionarse por error | Volver a agregar la exclusión |
| Las capturas de `docs/evidencias/capturas/D-1/login_*` son las de D-2 | La evidencia de D-1 queda mezclada | Regenerar con `CAPTURAS=1 pytest tests/e2e/test_interfaz_d1_e2e.py::test_generar_capturas` |
| Se eliminó `.gitlab-ci.yml` | Solo queda GitHub Actions | Ninguna, si GitLab ya no se usa |
| El CI instala `pytest`, `pytest-django` y `selenium` sin versión | El CI puede usar versiones distintas a las locales | Usar `pip install -r requirements-dev.txt` |

### c.5 Trabajo pendiente

| Prioridad | Tarea | Requisito |
|---|---|---|
| Alta | Etapa 5.2: permisos de creador, asignado (solo cambia el estado) y administrador; ruta `task-status`; formulario con asignado; `TaskCreate` debe guardar `created_by` | 3 |
| Alta | Etapa 6: perfil (nombre, apellido, correo) y cambio de contraseña con vistas nativas de Django | 6, 7 |
| Media | Filtro por estado (todas, pendientes, completadas) | 4 |
| Media | Rediseño D-3 a D-5 (lista, formularios, detalle, confirmación, verificación final) | – |
| Baja | Prueba para GET a `/register/` con sesión (línea 36 de `views.py`) | – |
| Baja | E-09: configuración segura para producción | – |

### c.6 Conclusiones

- Las pruebas encontraron un defecto crítico (E-01) que impedía ejecutar el sistema y que no se veía en el entorno local por el bytecode en caché. Ejecutar la suite en un clon limpio (CI) lo habría detectado antes.
- La prueba E2E inestable (E-10) muestra que una espera mal formulada puede pasar casi siempre y ocultar errores; repetir las pruebas varias veces fue lo que permitió encontrarla.
- Escribir primero la prueba de regresión y confirmar que falla antes de corregir dio evidencia objetiva de cada corrección.
- La migración de datos se trató como una operación de riesgo: copia verificada, ensayo sobre una copia y verificación posterior. No hubo pérdida de datos.
- La autorización entre usuarios funciona para el modelo actual (cada usuario solo ve sus tareas), pero la asignación a otros usuarios necesita la etapa 5.2 antes de considerarse completa.

---

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
