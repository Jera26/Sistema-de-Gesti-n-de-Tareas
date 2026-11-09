
import re
import subprocess
from pathlib import Path

import pytest
from django.urls import reverse
from base.models import Task

pytestmark = pytest.mark.django_db

BASE_DIR = Path(__file__).resolve().parent.parent


# E-02: el buscador conserva el texto buscado
def test_e02_busqueda_conserva_texto_en_contexto_y_campo(client_a, user_a):
    Task.objects.create(user=user_a, title="Comprar resina")
    r = client_a.get(reverse("tasks"), {"search-area": "resina"})
    assert r.context["search_input"] == "resina"
    assert 'name="search-area" value="resina"' in r.content.decode()


# E-03: pendientes y completadas usan iconos distintos
def test_e03_icono_distinto_para_pendiente_y_completada(client_a, user_a):
    Task.objects.create(user=user_a, title="Pendiente", complete=False)
    Task.objects.create(user=user_a, title="Hecha", complete=True)
    html = client_a.get(reverse("tasks")).content.decode()
    # Se cuentan los atributos class del marcado, no las reglas del CSS embebido
    assert html.count('class="task-incomplete-icon"') == 1
    assert html.count('class="task-complete-icon"') == 1


# E-04: sin comillas duplicadas en los enlaces ni entidades HTML sin cerrar
def test_e04_html_de_lista_sin_errores_de_sintaxis(client_a, user_a):
    Task.objects.create(user=user_a, title="Pendiente", complete=False)
    Task.objects.create(user=user_a, title="Hecha", complete=True)
    html = client_a.get(reverse("tasks")).content.decode()
    assert re.search(r'href="[^"]*""', html) is None
    assert re.search(r"&#215(?!;)", html) is None


# E-05: el detalle de tarea usa la plantilla base
def test_e05_detalle_extiende_plantilla_base(client_a, tarea_a):
    r = client_a.get(reverse("task", args=[tarea_a.pk]))
    assert "base/main.html" in [t.name for t in r.templates]


# E-06: un único elemento con name="description" en el formulario de tarea
def test_e06_un_solo_elemento_con_name_description(client_a):
    html = client_a.get(reverse("task-create")).content.decode()
    assert html.count('name="description"') == 1


# E-07: la base de datos local está ignorada y no versionada
def test_e07_db_sqlite3_ignorada_por_git():
    try:
        ignorado = subprocess.run(
            ["git", "check-ignore", "-q", "db.sqlite3"], cwd=BASE_DIR
        ).returncode
        versionado = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "db.sqlite3"],
            cwd=BASE_DIR, capture_output=True,
        ).returncode
    except FileNotFoundError:
        pytest.skip("git no está disponible")
    assert ignorado == 0, "db.sqlite3 no está en .gitignore"
    assert versionado != 0, "db.sqlite3 sigue versionado en git"
