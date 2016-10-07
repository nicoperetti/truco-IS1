from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max
from random import shuffle

from truco.models.Estadistica import Estadistica

from.constant import *


class Usuario(models.Model):
    class Meta:
        app_label = "truco"

    usuario = models.OneToOneField(User, primary_key=True)
    estadistica = models.ForeignKey('Estadistica', related_name='estadistica_user')
    partido = models.ForeignKey('Partido', related_name='usuarios')
    cantidad_partidas_ganadas = models.IntegerField(default=0)

    def incrementar(self):
        self.cantidad_partidas_ganadas += 1

    def __unicode__(self):
        return self.usuario
