"""D-1 – Estructura visual general: recursos estáticos propios, barra lateral,
barra superior, cierre de sesión por POST y ausencia de recursos externos."""
import re

import pytest
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.urls import reverse

pytestmark = pytest.mark.django_db

ESTATICOS = [
    "base/css/tokens.css",
    "base/css/app.css",
    "base/js/app.js",
    "base/img/logo.svg",
    "base/icons/sprite.svg",
]


def _html(cliente, nombre, *args):
    return cliente.get(reverse(nombre, args=args)).content.decode()


@pytest.mark.parametrize("ruta", ESTATICOS)
def test_recursos_estaticos_existen(ruta):
    assert finders.find(ruta), f"No se encontró {ruta}"


@pytest.mark.parametrize("nombre,con_pk,autenticado", [
    ("login", False, False), ("register", False, False),
    ("tasks", False, True), ("task", True, True), ("task-create", False, True),
    ("task-update", True, True), ("task-delete", True, True),
])
def test_paginas_sin_recursos_externos_ni_stitch(client, client_a, tarea_a, nombre, con_pk, autenticado):
    cliente = client_a if autenticado else client
    html = _html(cliente, nombre, *([tarea_a.pk] if con_pk else []))
    assert re.search(r'(src|href)="(https?:)?//', html) is None, "Hay recursos externos"
    for prohibido in ("cdn.tailwindcss.com", "googleapis", "googleusercontent", "stitch"):
        assert prohibido not in html.lower()
    assert "/static/base/css/tokens.css" in html
    assert "/static/base/css/app.css" in html
    assert "/static/base/js/app.js" in html


def test_sidebar_y_topbar_para_usuario_autenticado(client_a):
    html = _html(client_a, "tasks")
    assert 'id="sidebar"' in html
    assert 'class="topbar"' in html
    assert f'href="{reverse("tasks")}"' in html
    assert f'href="{reverse("task-create")}"' in html


def test_sin_sidebar_en_paginas_de_autenticacion(client):
    for nombre in ("login", "register"):
        html = _html(client, nombre)
        assert 'id="sidebar"' not in html and 'class="topbar"' not in html


@pytest.mark.parametrize("nombre,con_pk", [
    ("tasks", False), ("task", True), ("task-update", True), ("task-delete", True),
])
def test_mis_tareas_marcada_como_activa(client_a, tarea_a, nombre, con_pk):
    html = _html(client_a, nombre, *([tarea_a.pk] if con_pk else []))
    activo = re.search(r'<a class="sidebar__link" href="([^"]+)" aria-current="page">', html)
    assert activo and activo.group(1) == reverse("tasks")


def test_nueva_tarea_marcada_como_activa(client_a):
    html = _html(client_a, "task-create")
    activo = re.search(r'<a class="sidebar__link" href="([^"]+)" aria-current="page">', html)
    assert activo and activo.group(1) == reverse("task-create")


def test_cierre_de_sesion_es_formulario_post_con_csrf(client_a):
    html = _html(client_a, "tasks")
    form = re.search(
        r'<form method="post" action="%s">(.*?)</form>' % re.escape(reverse("logout")), html, re.S)
    assert form, "No hay formulario POST de cierre de sesión"
    assert 'name="csrfmiddlewaretoken"' in form.group(1)
    assert 'type="submit"' in form.group(1)


def test_no_quedan_enlaces_get_de_cierre_de_sesion(client_a, tarea_a):
    for nombre, args in (("tasks", []), ("task", [tarea_a.pk]), ("task-create", [])):
        assert f'href="{reverse("logout")}"' not in _html(client_a, nombre, *args)


def test_cierre_de_sesion_por_post_termina_la_sesion(client_a):
    r = client_a.post(reverse("logout"))
    assert r.status_code == 302 and r.url == reverse("login")
    assert client_a.get(reverse("tasks")).status_code == 302


def test_topbar_muestra_usuario_real(client_a):
    html = _html(client_a, "tasks")
    assert "alice" in html
    assert "Administrador" not in html


def test_topbar_muestra_nombre_completo_y_rol_admin(client):
    admin = User.objects.create_user("jefa", password="Pass12345!", first_name="Ana",
                                     last_name="Ruiz", is_staff=True)
    client.force_login(admin)
    html = _html(client, "tasks")
    assert "Ana Ruiz" in html and "Administrador" in html
    assert f'href="{reverse("admin:index")}"' in html


def test_enlace_admin_oculto_para_usuario_normal(client_a):
    assert f'href="{reverse("admin:index")}"' not in _html(client_a, "tasks")


def test_titulo_de_seccion_en_topbar_y_documento(client_a):
    html = _html(client_a, "task-create")
    assert "<title>Nueva tarea · Plásticos Sustentables</title>" in html
    assert '<li aria-current="page">Nueva tarea</li>' in html


def test_accesibilidad_basica(client_a):
    html = _html(client_a, "tasks")
    assert 'href="#contenido"' in html and 'id="contenido"' in html
    assert 'aria-controls="sidebar"' in html and 'aria-expanded="false"' in html
    assert 'aria-label="Abrir menú"' in html
    # Todos los iconos SVG están ocultos para lectores de pantalla.
    assert html.count('class="icono"') == html.count('class="icono" aria-hidden="true"')


def test_bloques_de_contenido_se_conservan(client_a, tarea_a):
    html = _html(client_a, "task-update", tarea_a.pk)
    assert 'name="csrfmiddlewaretoken"' in html
    assert 'name="title"' in html and 'name="description"' in html and 'name="complete"' in html
