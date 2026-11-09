import pytest
from django.urls import reverse
from base.models import Task

pytestmark = pytest.mark.django_db


def test_editar_tarea_propia(client_a, tarea_a):
    client_a.post(reverse("task-update", args=[tarea_a.pk]),
                  {"title": "Editada", "description": "", "complete": "on"})
    tarea_a.refresh_from_db()
    assert tarea_a.title == "Editada" and tarea_a.complete is True

def test_contador_cuenta_solo_pendientes(client_a, user_a):
    Task.objects.create(user=user_a, title="P1", complete=False)
    Task.objects.create(user=user_a, title="P2", complete=False)
    Task.objects.create(user=user_a, title="C1", complete=True)
    r = client_a.get(reverse("tasks"))
    assert r.context["count"] == 2

def test_crear_tarea_sin_titulo_es_rechazada(client_a):
    r = client_a.post(reverse("task-create"), {"title": ""})
    assert r.status_code == 200 and Task.objects.count() == 0

def test_logout(client_a):
    r = client_a.post(reverse("logout"))
    assert r.status_code == 302