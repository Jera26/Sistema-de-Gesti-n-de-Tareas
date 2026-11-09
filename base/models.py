from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='usuario')
    title = models.CharField('título', max_length=200)
    description = models.TextField('descripción', null=True, blank=True)
    complete = models.BooleanField('completada', default=False)
    created = models.DateTimeField('creada', auto_now_add=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['complete']
        verbose_name = 'tarea'
        verbose_name_plural = 'tareas'
