"""Etapa 5.1 – Migraciones 0003 (created_by) y 0004 (copia de datos).

Se ejecutan migraciones reales sobre la base de pruebas con MigrationExecutor:
se crean filas con el esquema anterior y se verifica el resultado tras migrar.
"""
import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

pytestmark = pytest.mark.django_db(transaction=True)

M0002 = ("base", "0002_etiquetas_en_espanol")
M0003 = ("base", "0003_task_created_by")
M0004 = ("base", "0004_copiar_user_a_created_by")


def _migrar(destino):
    executor = MigrationExecutor(connection)
    executor.loader.build_graph()
    executor.migrate([destino])
    return executor.loader.project_state([destino]).apps


@pytest.fixture
def migrador():
    yield _migrar
    # Deja la base en la última migración para el resto de la suite.
    executor = MigrationExecutor(connection)
    executor.loader.build_graph()
    executor.migrate(executor.loader.graph.leaf_nodes())


def _columnas_task():
    with connection.cursor() as c:
        return {col.name for col in connection.introspection.get_table_description(c, "base_task")}


def test_0003_agrega_columna_created_by(migrador):
    migrador(M0002)
    assert "created_by_id" not in _columnas_task()
    migrador(M0003)
    assert "created_by_id" in _columnas_task()


def test_0004_copia_user_en_created_by_sin_perder_datos(migrador):
    apps = migrador(M0002)
    User = apps.get_model("auth", "User")
    Task = apps.get_model("base", "Task")
    alice = User.objects.create(username="alice")
    bob = User.objects.create(username="bob")
    filas = [
        Task.objects.create(user=alice, title="A1", description="d1", complete=False),
        Task.objects.create(user=alice, title="A2", description=None, complete=True),
        Task.objects.create(user=bob, title="B1", description="d3", complete=False),
        Task.objects.create(user=None, title="Sin usuario", complete=False),
    ]
    antes = {t.pk: (t.title, t.description, t.complete, t.user_id, t.created) for t in filas}

    apps = migrador(M0004)
    Task = apps.get_model("base", "Task")
    assert Task.objects.count() == len(filas)
    for t in Task.objects.all():
        titulo, descripcion, completa, user_id, creada = antes[t.pk]
        assert (t.title, t.description, t.complete, t.user_id, t.created) == (
            titulo, descripcion, completa, user_id, creada)
        assert t.created_by_id == user_id  # None se mantiene None


def test_0004_no_sobrescribe_created_by_existente(migrador):
    apps = migrador(M0003)
    User = apps.get_model("auth", "User")
    Task = apps.get_model("base", "Task")
    alice = User.objects.create(username="alice")
    bob = User.objects.create(username="bob")
    t = Task.objects.create(user=bob, created_by=alice, title="Asignada por Alice")

    apps = migrador(M0004)
    t = apps.get_model("base", "Task").objects.get(pk=t.pk)
    assert t.created_by_id == alice.pk and t.user_id == bob.pk


def test_migraciones_reversibles_conservan_datos(migrador):
    apps = migrador(M0002)
    User = apps.get_model("auth", "User")
    Task = apps.get_model("base", "Task")
    alice = User.objects.create(username="alice")
    t = Task.objects.create(user=alice, title="Persistente", complete=True)

    migrador(M0004)
    apps = migrador(M0002)
    assert "created_by_id" not in _columnas_task()
    t = apps.get_model("base", "Task").objects.get(pk=t.pk)
    assert (t.title, t.complete, t.user_id) == ("Persistente", True, alice.pk)
