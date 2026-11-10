# a) Código fuente del sistema

> Sistema de Gestión de Tareas – Plásticos Sustentables · Autora: Jeraldin Caliz · Corte: 9 de noviembre de 2026 · Rama `feature/pruebas-qa` (commit `faa6169`)
>
> Documentos de la entrega: [a) Código fuente](a_codigo_fuente.md) · [b) Documentación de las pruebas](b_documentacion_pruebas.md) · [c) Informe final](c_informe_final.md)

| Dato | Valor |
|---|---|
| Entorno | Windows, Python 3.10.6, Django 4.1.5, SQLite |
| Herramientas de prueba | pytest 9.2.0, pytest-django 4.14.0, pytest-cov 7.1.0, Selenium 4.52.0, Chrome 156 |

## a.1 Descripción

Aplicación web Django para que los empleados de Plásticos Sustentables registren y gestionen tareas. Permite registrarse, iniciar y cerrar sesión, crear, ver, editar, eliminar y buscar tareas, y distinguir las tareas pendientes de las completadas. Cada usuario solo accede a sus propias tareas.

El código fuente completo está en el repositorio Git. Esta sección describe su organización e incluye los archivos principales del backend.

## a.2 Estructura del proyecto

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

## a.3 Modelo de datos

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

## a.4 Rutas (`base/urls.py`)

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

## a.5 Vistas (`base/views.py`)

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

## a.6 Regla de eliminación de usuarios (`base/signals.py`)

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

## a.7 Interfaz

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

## a.8 Cobertura de los requisitos funcionales

| # | Requisito | Estado |
|---|---|---|
| 1 | Registro e inicio de sesión | Implementado y probado |
| 2 | Crear, editar y eliminar tareas | Implementado y probado |
| 3 | Asignación de tareas a usuarios | Parcial: modelo y migración listos (etapa 5.1); faltan vistas y permisos (etapa 5.2) |
| 4 | Filtrado y búsqueda | Parcial: búsqueda por título; falta filtro por estado |
| 5 | Ver pendientes y completadas | Implementado: indicador de estado y contador de pendientes |
| 6 | Gestión de perfiles | No implementado (etapa 6) |
| 7 | Editar perfil y cambiar contraseña | No implementado (etapa 6) |
