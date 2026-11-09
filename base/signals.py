"""Regla de eliminación de usuarios (decisión C1).

`Task.created_by` y `Task.user` usan SET_NULL. Sin esta regla, una tarea cuyo
único usuario se elimina quedaría huérfana (sin creador ni asignado).

Funcionamiento, dentro de la misma transacción del borrado de Django:
1. pre_delete: se guardan los IDs de las tareas vinculadas al usuario.
2. Django aplica SET_NULL y borra el usuario.
3. post_delete: de esas tareas, se eliminan solo las que quedaron sin
   creador y sin asignado.

Así no se tocan tareas de otros usuarios ni tareas huérfanas previas, y el
borrado masivo de varios usuarios funciona (post_delete se ejecuta después de
aplicar todos los SET_NULL).
"""
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver

from .models import Task

_ATRIBUTO = '_tareas_vinculadas_ids'


@receiver(pre_delete, sender=User, dispatch_uid='base_tareas_vinculadas_pre_delete')
def guardar_tareas_vinculadas(sender, instance, **kwargs):
    ids = Task.objects.filter(
        Q(created_by=instance) | Q(user=instance)
    ).values_list('pk', flat=True)
    setattr(instance, _ATRIBUTO, list(ids))


@receiver(post_delete, sender=User, dispatch_uid='base_tareas_huerfanas_post_delete')
def eliminar_tareas_huerfanas(sender, instance, **kwargs):
    ids = getattr(instance, _ATRIBUTO, None)
    if ids:
        Task.objects.filter(
            pk__in=ids, created_by__isnull=True, user__isnull=True
        ).delete()
