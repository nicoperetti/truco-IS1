from django.db import models

from.constant import *


class Carta(models.Model):
    class Meta:
        app_label = "truco"

    jugador = models.ForeignKey('Jugador',related_name = 'cartas')
    ronda = models.ForeignKey('Ronda',related_name = 'cartas_de_la_ronda')
    ide = models.PositiveIntegerField()
    palo = models.PositiveIntegerField()
    valor = models.PositiveIntegerField()
    power = models.PositiveIntegerField()
    jugada = models.BooleanField(default=False)
    tirada_en_vuelta = models.PositiveIntegerField(default=0)
    imagen = models.CharField(max_length=100, blank=True)

    def get_jugador(self):
        return self.jugador

    def set_jugada(self, estado):
        if not self.jugada:
            self.jugada = True
            self.tirada_en_vuelta = estado
            self.save()

    def set_image(self):
        cadena = '/static/mazo/' + str(self.ide) + '.jpg'
        self.imagen = cadena

    def __unicode__(self):
        return str(self.ide)
