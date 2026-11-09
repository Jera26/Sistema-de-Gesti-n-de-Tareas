"""Pruebas de la interfaz en español (etapa 4)."""
import re

import pytest
from django.conf import settings
from django.urls import reverse
from base.models import Task

pytestmark = pytest.mark.django_db

TEXTOS_EN_INGLES = [
    "Hello", "pending task", "Logout", "Log In", "Login", "Search",
    "No items in list", "Back", "Submit", "Delete", "Register",
    "Are you sure", "Don't have an account", "Already have an account",
    "Title:", "Description:", "Complete:", "Task:",
]


def _texto_visible(html):
    """Quita <style>, <script> y etiquetas para revisar solo el texto mostrado."""
    html = re.sub(r"<(style|script)\b.*?</\1>", "", html, flags=re.S)
    html = re.sub(r'value="([^"]*)"', r" \1 ", html)  # conserva el texto de botones
    return re.sub(r"<[^>]+>", " ", html)


def _sin_ingles(html):
    texto = _texto_visible(html)
    return [t for t in TEXTOS_EN_INGLES if t in texto]


def test_language_code_es():
    assert settings.LANGUAGE_CODE == "es"


def test_html_declara_idioma_es(client):
    assert '<html lang="es">' in client.get(reverse("login")).content.decode()


@pytest.mark.parametrize("nombre", ["login", "register"])
def test_paginas_publicas_sin_textos_en_ingles(client, nombre):
    assert _sin_ingles(client.get(reverse(nombre)).content.decode()) == []


@pytest.mark.parametrize("nombre,con_pk", [
    ("tasks", False), ("task", True), ("task-create", False),
    ("task-update", True), ("task-delete", True),
])
def test_paginas_privadas_sin_textos_en_ingles(client_a, tarea_a, nombre, con_pk):
    url = reverse(nombre, args=[tarea_a.pk] if con_pk else [])
    assert _sin_ingles(client_a.get(url).content.decode()) == []


def test_etiquetas_del_formulario_de_tarea(client_a):
    html = client_a.get(reverse("task-create")).content.decode()
    for etiqueta in ("Título", "Descripción", "Completada"):
        assert etiqueta in html


def test_lista_vacia_en_espanol(client_a):
    assert "No hay tareas" in client_a.get(reverse("tasks")).content.decode()


@pytest.mark.parametrize("pendientes,esperado", [
    (1, "1 tarea pendiente"), (2, "2 tareas pendientes"), (0, "0 tareas pendientes"),
])
def test_contador_con_plural_en_espanol(client_a, user_a, pendientes, esperado):
    for i in range(pendientes):
        Task.objects.create(user=user_a, title=f"P{i}")
    texto = " ".join(_texto_visible(client_a.get(reverse("tasks")).content.decode()).split())
    assert esperado in texto


def test_validacion_registro_en_espanol(client):
    r = client.post(reverse("register"), {
        "username": "nuevo", "password1": "Pass12345!", "password2": "Otra12345!"})
    assert "Los dos campos de contraseña no coinciden." in r.content.decode()


def test_validacion_login_en_espanol(client):
    r = client.post(reverse("login"), {"username": "x", "password": "y"})
    assert "Por favor, introduzca un nombre de usuario y clave correctos" in r.content.decode()


def test_validacion_titulo_obligatorio_en_espanol(client_a):
    r = client_a.post(reverse("task-create"), {"title": ""})
    assert "Este campo es obligatorio." in r.content.decode()
