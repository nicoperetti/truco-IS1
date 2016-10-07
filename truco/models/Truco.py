from django.db import models

from.constant import *


class Truco(models.Model):
    class Meta:
        app_label = "truco"

    ronda = models.ForeignKey('Ronda',related_name = 'truco_de_ronda')
    # nivel actual de truco eg Retruco querido
    nivel = models.PositiveIntegerField(default = NADA)
    # siguiente nivel eg Vale cuatro
    siguiente_nivel = models.PositiveIntegerField(default = NADA)
    # Que equipo canto truco(int 1 o 2)
    quien_canto = models.PositiveIntegerField(default = NINGUNO)
    # Estados: inicial, esperando, aceptado, rechazado, calculado
    estado = models.IntegerField(default = INICIAL)

    def puede_cantar_truco(self, numero_equipo):
        if self.quien_canto != numero_equipo and self.estado != RECHAZADO:
            return True

    def procesar_input(self, numero_equipo, accion):
        if accion == "": # Se canta truco por primera vez
            self.siguiente_nivel = TRUCO
            self.quien_canto = numero_equipo
            self.estado = ESPERANDO

        elif accion == "retruco":
            self.siguiente_nivel = RETRUCO
            self.quien_canto = numero_equipo
            self.estado = ESPERANDO

        elif accion == "vale_cuatro":
            self.siguiente_nivel = VALE_CUATRO
            self.quien_canto = numero_equipo
            self.estado = ESPERANDO

        elif accion == "quiero":
            self.nivel = self.siguiente_nivel
            self.estado = ACEPTADO

        elif accion == "noquiero":
            self.estado = RECHAZADO

        elif accion == "mevoyalmazo":
            self.quien_canto = numero_equipo
            self.estado = ME_VOY_AL_MAZO
        self.save()

    def get_puntos_truco(self):
        return self.nivel

    def mostrar_boton_truco(self, numero_equipo , numero_jugador):
        ronda = self.ronda
        boton_quiero_truco = self.quien_canto != numero_equipo and self.estado==ESPERANDO
        if self.estado != ESPERANDO:
            if self.siguiente_nivel == NADA and ( ronda.quienjuega == numero_jugador)  :
                result = {'truco':True,'retruco':False,'vale_cuatro':False,'boton_quiero_truco':boton_quiero_truco}
            elif self.siguiente_nivel == TRUCO and self.quien_canto!=numero_equipo:
                result = {'truco':False,'retruco':True,'vale_cuatro':False,'boton_quiero_truco':boton_quiero_truco}
            elif self.siguiente_nivel == RETRUCO and self.quien_canto!=numero_equipo:
                result = {'truco':False,'retruco':False,'vale_cuatro':True,'boton_quiero_truco':boton_quiero_truco}
            else:
                result = {'truco':False,'retruco':False,'vale_cuatro':False,'boton_quiero_truco':boton_quiero_truco}
        else:
            result = {'truco':False,'retruco':( boton_quiero_truco and self.siguiente_nivel<3),'vale_cuatro':  ( boton_quiero_truco and self.siguiente_nivel<4),'boton_quiero_truco':boton_quiero_truco}
        return result
