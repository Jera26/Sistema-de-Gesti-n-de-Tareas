import pytest
from base.models import Task
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_crear_tarea_asigna_usuario_actual(client_a, user_a):
    client_a.post(reverse("task-create"), {"title": "Nueva", "description": "x"})
    assert Task.objects.get(title="Nueva").user == user_a


def test_lista_muestra_solo_tareas_propias(client_a, tarea_a, user_b):
    Task.objects.create(user=user_b, title="Tarea de Bob")
    r = client_a.get(reverse("tasks"))
    titulos = [t.title for t in r.context["tasks"]]
    assert titulos == ["Tarea de Alice"]


def test_busqueda_por_titulo(client_a, user_a):
    Task.objects.create(user=user_a, title="Comprar resina")
    Task.objects.create(user=user_a, title="Revisar moldes")
    r = client_a.get(reverse("tasks"), {"search-area": "resina"})
    assert [t.title for t in r.context["tasks"]] == ["Comprar resina"]


def test_eliminar_tarea_propia(client_a, tarea_a):
    client_a.post(reverse("task-delete", args=[tarea_a.pk]))
    assert not Task.objects.filter(pk=tarea_a.pk).exists()


def test_cascade_al_borrar_usuario(user_a, tarea_a):
    user_a.delete()
    assert Task.objects.count() == 0


# --- Pruebas de autorización: HOY FALLAN y evidencian los defectos ---

def test_no_puede_ver_tarea_ajena(client_b, tarea_a):
    r = client_b.get(reverse("task", args=[tarea_a.pk]))
    assert r.status_code in (403, 404)


def test_no_puede_eliminar_tarea_ajena(client_b, tarea_a):
    client_b.post(reverse("task-delete", args=[tarea_a.pk]))
    assert Task.objects.filter(pk=tarea_a.pk).exists()


def test_no_puede_editar_tarea_ajena(client_b, tarea_a):
    client_b.post(reverse("task-update", args=[tarea_a.pk]), {"title": "Hackeada"})
    tarea_a.refresh_from_db()
    assert tarea_a.title == "Tarea de Alice"


def test_no_puede_reasignar_tarea_a_otro_usuario(client_a, tarea_a, user_a, user_b):
    client_a.post(reverse("task-update", args=[tarea_a.pk]),
                  {"title": "Tarea de Alice", "user": user_b.pk})
    tarea_a.refresh_from_db()
    assert tarea_a.user == user_a