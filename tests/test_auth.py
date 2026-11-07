import pytest
from django.contrib.auth.models import User
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_registro_exitoso_crea_usuario_y_redirige(client):
    r = client.post(reverse("register"), {
        "username": "nuevo", "password1": "Pass12345!", "password2": "Pass12345!"})
    assert r.status_code == 302
    assert User.objects.filter(username="nuevo").exists()


def test_registro_con_contrasenas_distintas_falla(client):
    r = client.post(reverse("register"), {
        "username": "nuevo", "password1": "Pass12345!", "password2": "Otra12345!"})
    assert r.status_code == 200
    assert not User.objects.filter(username="nuevo").exists()


def test_registro_usuario_duplicado_falla(client, user_a):
    r = client.post(reverse("register"), {
        "username": "alice", "password1": "Pass12345!", "password2": "Pass12345!"})
    assert r.status_code == 200
    assert User.objects.filter(username="alice").count() == 1


def test_login_correcto(client, user_a):
    r = client.post(reverse("login"), {"username": "alice", "password": "Pass12345!"})
    assert r.status_code == 302


def test_login_con_contrasena_incorrecta(client, user_a):
    r = client.post(reverse("login"), {"username": "alice", "password": "mala"})
    assert r.status_code == 200


def test_lista_requiere_sesion(client):
    r = client.get(reverse("tasks"))
    assert r.status_code == 302
    assert "login" in r.url