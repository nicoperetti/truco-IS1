from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max
from random import shuffle

#from truco.models.Usuario import Usuario

from.constant import *


class Estadistica(models.Model):
    ide = models.AutoField(primary_key=True)
    class Meta:
        app_label = "truco"

    def datos(self):
        data = {}
        usuario = self.estadistica_user.all()
#        for i in usuario:
#            data = dict(data.item() + {'i': i.cantidad_partidas_ganadas}.item())
        data = {'usuarios':usuario}
        return data

