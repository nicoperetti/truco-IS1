from django.db import models
from django.contrib.auth.models import User

from truco.models.Jugador import Jugador

from.constant import *


class Equipo(models.Model):
    class Meta:
        app_label = "truco"

    numero = models.IntegerField(default = 1)
    cantidad_jugadores = models.IntegerField(default = 0)
    total_de_jugadores = models.IntegerField(default = 1)
    partido = models.ForeignKey('Partido',related_name = 'equipos')

    def get_numero(self):
        return self.numero


    def crear_jugador(self,user,numero_jugador):
        if self.cantidad_jugadores < self.total_de_jugadores:
            jugadornuevo = Jugador(usuario = user, equipo = self ,numero = numero_jugador)
            jugadornuevo.save()
            self.cantidad_jugadores += 1
            self.save()

    def esta_lleno(self):
        return self.cantidad_jugadores == self.total_de_jugadores

    def obtener_jugadores(self ):
        return self.jugadores_del_equipo.all()
    def __unicode__(self):              # __unicode__ on Python 2
        return str(self.numero)
        
