import pytest
from django.contrib.auth.models import User
from django.test import Client
from base.models import Task

PASSWORD = "Pass12345!"


@pytest.fixture
def user_a(db):
    return User.objects.create_user("alice", password=PASSWORD)


@pytest.fixture
def user_b(db):
    return User.objects.create_user("bob", password=PASSWORD)


@pytest.fixture
def client_a(user_a):
    c = Client()
    c.force_login(user_a)
    return c


@pytest.fixture
def client_b(user_b):
    c = Client()
    c.force_login(user_b)
    return c


@pytest.fixture
def tarea_a(user_a):
    return Task.objects.create(user=user_a, title="Tarea de Alice", complete=False)