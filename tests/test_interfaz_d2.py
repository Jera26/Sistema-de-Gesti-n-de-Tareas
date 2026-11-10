
import re

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

CAMPOS = {
    "login": ["id_username", "id_password"],
    "register": ["id_username", "id_password1", "id_password2"],
}


def _html(client, nombre, datos=None):
    r = client.post(reverse(nombre), datos) if datos is not None else client.get(reverse(nombre))
    return r.content.decode()


def _bloque_de_campo(html, campo_id):
    """Devuelve el <div class="field..." data-field> que contiene el campo."""
    for bloque in re.findall(r'<div class="field[^"]*" data-field>.*?\n</div>', html, re.S):
        if f'id="{campo_id}"' in bloque:
            return bloque
    return None


@pytest.mark.parametrize("nombre", ["login", "register"])
def test_usa_diseno_de_tarjeta_y_no_el_anterior(client, nombre):
    html = _html(client, nombre)
    assert 'class="auth-card"' in html and 'class="auth-panel"' in html
    assert "header-bar" not in html and "card-body" not in html and "form.as_p" not in html


@pytest.mark.parametrize("nombre", ["login", "register"])
def test_cada_campo_tiene_etiqueta_asociada(client, nombre):
    html = _html(client, nombre)
    for campo_id in CAMPOS[nombre]:
        assert f'<label for="{campo_id}">' in html
        assert f'id="{campo_id}"' in html


@pytest.mark.parametrize("nombre,names", [
    ("login", ["username", "password"]),
    ("register", ["username", "password1", "password2"]),
])
def test_conserva_names_csrf_y_metodo_post(client, nombre, names):
    html = _html(client, nombre)
    assert '<form method="POST" class="form">' in html
    assert 'name="csrfmiddlewaretoken"' in html
    for name in names:
        assert f'name="{name}"' in html


def test_conserva_autocompletado_de_django(client):
    login = _html(client, "login")
    assert 'autocomplete="username"' in login and 'autocomplete="current-password"' in login
    registro = _html(client, "register")
    assert registro.count('autocomplete="new-password"') == 2


@pytest.mark.parametrize("nombre", ["login", "register"])
def test_campos_obligatorios_marcados(client, nombre):
    html = _html(client, nombre)
    assert html.count('class="field__required"') == len(CAMPOS[nombre])
    assert html.count(" required ") + html.count(" required>") >= len(CAMPOS[nombre])


@pytest.mark.parametrize("nombre", ["login", "register"])
def test_boton_mostrar_contrasena_por_cada_campo_password(client, nombre):
    html = _html(client, nombre)
    botones = re.findall(r'<button class="field__toggle"[^>]*>', html)
    controlados = sorted(re.search(r'aria-controls="([^"]+)"', b).group(1) for b in botones)
    assert controlados == sorted(c for c in CAMPOS[nombre] if "password" in c)
    for b in botones:
        assert 'type="button"' in b and 'aria-pressed="false"' in b and "hidden" in b


def test_ayuda_de_django_se_muestra_en_registro(client):
    html = _html(client, "register")
    assert 'id="id_username_ayuda"' in html
    assert 'id="id_password1_ayuda"' in html


def test_error_de_contrasenas_distintas_junto_al_campo(client):
    html = _html(client, "register", {
        "username": "nuevo", "password1": "Pass12345!", "password2": "Otra12345!"})
    bloque = _bloque_de_campo(html, "id_password2")
    assert bloque and "field--error" in bloque
    assert 'id="id_password2_errores"' in bloque
    assert "Los dos campos de contraseña no coinciden." in bloque


def test_error_de_usuario_duplicado_junto_al_campo(client, user_a):
    html = _html(client, "register", {
        "username": "alice", "password1": "Pass12345!", "password2": "Pass12345!"})
    bloque = _bloque_de_campo(html, "id_username")
    assert bloque and "field--error" in bloque and 'id="id_username_errores"' in bloque


def test_error_general_de_login_en_errorlist(client, user_a):
    html = _html(client, "login", {"username": "alice", "password": "mala"})
    assert re.search(r'<ul class="errorlist nonfield"><li>Por favor, introduzca', html)


def test_valor_ingresado_se_conserva_tras_error(client, user_a):
    html = _html(client, "login", {"username": "alice", "password": "mala"})
    assert re.search(r'name="username" value="alice"', html)


def test_enlaces_cruzados(client):
    assert f'href="{reverse("register")}">Regístrate</a>' in _html(client, "login")
    assert f'href="{reverse("login")}">Inicia sesión</a>' in _html(client, "register")


@pytest.mark.parametrize("nombre", ["login", "register"])
def test_no_inventa_funcionalidades(client, nombre):
    html = _html(client, nombre).lower()
    for texto in ("recordarme", "olvidaste", "términos", "privacidad", "correo electrónico",
                  "nombre completo", "2fa", "%", "tls"):
        assert texto not in html, texto


def test_panel_describe_solo_funciones_reales(client):
    html = _html(client, "login")
    panel = re.search(r'<aside class="auth-panel".*?</aside>', html, re.S).group(0)
    for texto in ("Crea, edita y elimina tareas.", "Busca tareas por su título.",
                  "Distingue las pendientes de las completadas."):
        assert texto in panel


def test_registro_y_login_siguen_funcionando(client):
    r = client.post(reverse("register"), {
        "username": "nueva", "password1": "Pass12345!", "password2": "Pass12345!"})
    assert r.status_code == 302 and r.url == reverse("tasks")
    client.post(reverse("logout"))
    r = client.post(reverse("login"), {"username": "nueva", "password": "Pass12345!"})
    assert r.status_code == 302
