"""Etapa 5.1 – Regla de eliminación de usuarios (decisión C1).

`created_by` y `user` usan SET_NULL. Al eliminar un usuario solo se borran las
tareas vinculadas a él que quedarían sin creador y sin asignado.
"""
import pytest
from django.contrib.auth.models import User
from django.db import models
from base.models import Task

pytestmark = pytest.mark.django_db

PASSWORD = "Pass12345!"


@pytest.fixture
def carol(db):
    return User.objects.create_user("carol", password=PASSWORD)


def _existe(tarea):
    return Task.objects.filter(pk=tarea.pk).exists()


# --- Configuración del modelo -------------------------------------------------

def test_created_by_y_user_usan_set_null():
    assert Task._meta.get_field("created_by").remote_field.on_delete is models.SET_NULL
    assert Task._meta.get_field("user").remote_field.on_delete is models.SET_NULL


def test_created_by_y_user_son_opcionales():
    for nombre in ("created_by", "user"):
        campo = Task._meta.get_field(nombre)
        assert campo.null and campo.blank


def test_related_names_distintos(user_a):
    t = Task.objects.create(created_by=user_a, user=user_a, title="X")
    assert list(user_a.tareas_creadas.all()) == [t]
    assert list(user_a.tareas_asignadas.all()) == [t]


def test_created_by_no_se_asigna_implicitamente(user_a):
    # Decisión C2: la relación creador/asignado es explícita; el modelo no la deduce.
    assert Task.objects.create(user=user_a, title="X").created_by is None


# --- Escenarios de eliminación -----------------------------------------------

def test_tarea_personal_se_elimina_con_su_usuario(user_a):
    t = Task.objects.create(created_by=user_a, user=user_a, title="Personal")
    user_a.delete()
    assert not _existe(t)


def test_eliminar_creador_conserva_tarea_asignada_a_otro(user_a, user_b):
    t = Task.objects.create(created_by=user_a, user=user_b, title="Para Bob")
    user_a.delete()
    t.refresh_from_db()
    assert t.created_by is None and t.user == user_b


def test_eliminar_asignado_conserva_tarea_del_creador(user_a, user_b):
    t = Task.objects.create(created_by=user_a, user=user_b, title="Para Bob")
    user_b.delete()
    t.refresh_from_db()
    assert t.created_by == user_a and t.user is None


def test_eliminar_creador_sin_asignado_elimina_tarea(user_a):
    t = Task.objects.create(created_by=user_a, user=None, title="Sin asignar")
    user_a.delete()
    assert not _existe(t)


def test_eliminar_asignado_sin_creador_elimina_tarea(user_a):
    t = Task.objects.create(created_by=None, user=user_a, title="Sin creador")
    user_a.delete()
    assert not _existe(t)


def test_no_afecta_tareas_de_otros_usuarios(user_a, user_b):
    Task.objects.create(created_by=user_a, user=user_a, title="De Alice")
    de_bob = Task.objects.create(created_by=user_b, user=user_b, title="De Bob")
    user_a.delete()
    de_bob.refresh_from_db()
    assert de_bob.created_by == user_b and de_bob.user == user_b


def test_no_borra_tareas_huerfanas_previas_no_vinculadas(user_a):
    # Una tarea que ya estaba sin usuarios no pertenece a alice: no se toca.
    huerfana = Task.objects.create(created_by=None, user=None, title="Huérfana previa")
    user_a.delete()
    assert _existe(huerfana)


def test_eliminacion_masiva_borra_solo_las_que_quedan_huerfanas(user_a, user_b, carol):
    entre_ambos = Task.objects.create(created_by=user_a, user=user_b, title="A→B")
    para_carol = Task.objects.create(created_by=user_a, user=carol, title="A→C")
    User.objects.filter(pk__in=[user_a.pk, user_b.pk]).delete()
    assert not _existe(entre_ambos)
    para_carol.refresh_from_db()
    assert para_carol.created_by is None and para_carol.user == carol


def test_eliminar_usuario_sin_tareas_no_borra_nada(user_a, user_b):
    t = Task.objects.create(created_by=user_b, user=user_b, title="De Bob")
    user_a.delete()
    assert Task.objects.count() == 1 and _existe(t)
