from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max

from truco.models.Carta import Carta

from.constant import *


class Jugador(models.Model):
    class Meta:
        app_label = "truco"

    usuario = models.OneToOneField(User, primary_key=True)
    equipo = models.ForeignKey('Equipo', related_name='jugadores_del_equipo')
    numero = models.PositiveIntegerField(default=0)
    puntos_cantados = models.IntegerField(default=-1)


    def get_numero_jugador(self):
        return self.numero

    def get_numero_equipo(self):
        return self.equipo.get_numero()

    def jugar_carta(self, ide, ronda):
        carta = self.cartas.filter(ide=ide)
        carta = carta[0]
        result = False
        if not carta.jugada:
            carta.set_jugada(ronda)
            carta.save()
            result = True
        return result

    def recibir_cartas(self, ron,a, b, c):
        carta1 = Carta(jugador=self,ronda = ron, ide=CARTAS[a][IDE], palo=CARTAS[a][PALO], valor=CARTAS[a][VALOR], power=CARTAS[a][POWER], jugada=False)
        carta1.set_image()
        carta1.save()
        carta2 = Carta(jugador=self,ronda = ron, ide=CARTAS[b][IDE], palo=CARTAS[b][PALO], valor=CARTAS[b][VALOR], power=CARTAS[b][POWER], jugada=False)
        carta2.set_image()
        carta2.save()
        carta3 = Carta(jugador=self,ronda = ron, ide=CARTAS[c][IDE], palo=CARTAS[c][PALO], valor=CARTAS[c][VALOR], power=CARTAS[c][POWER], jugada=False)
        carta3.set_image()
        carta3.save()
        # Puntos para el envido
        cartas = [carta1, carta2, carta3]
        pts = []
        for i in range(0, len(cartas)):
            # Calculo los puntos de las cartas individuales.
            if cartas[i].valor not in CARTAS_NEGRAS:
                vali = cartas[i].valor
            else:
                vali = 0
            pts.append(vali)
            for j in range(i + 1, len(cartas)):
                # Calculo los puntos de los pares de cartas.
                if cartas[i].palo == cartas[j].palo:
                    if cartas[j].valor not in CARTAS_NEGRAS:
                        valj = cartas[j].valor
                    else:
                        valj = 0
                    pts.append(20 + vali + valj)
        # puntos_envido = mayor de los puntajes (entre cartas y pares de cartas).
        self.puntos_envido = max(pts)
        self.save()

    def __unicode__(self):              # __unicode__ on Python 2
        return self.usuario.get_username()
