import pytest
from django.core.exceptions import ValidationError
from base.models import Task

pytestmark = pytest.mark.django_db

def test_str_devuelve_el_titulo(tarea_a):
    assert str(tarea_a) == "Tarea de Alice"

def test_complete_es_false_por_defecto(user_a):
    assert Task.objects.create(user=user_a, title="X").complete is False

def test_titulo_de_mas_de_200_caracteres_no_valida(user_a):
    t = Task(user=user_a, title="a" * 201)
    with pytest.raises(ValidationError):
        t.full_clean()

def test_titulo_vacio_no_valida(user_a):
    with pytest.raises(ValidationError):
        Task(user=user_a, title="").full_clean()