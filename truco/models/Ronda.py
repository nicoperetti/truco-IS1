from django.db import models
from django.db.models import Min, Max

from truco.models.Envido import Envido
from truco.models.Truco import Truco

from.constant import *


class Ronda(models.Model):
    class Meta:
        app_label = "truco"

    partido = models.ForeignKey('Partido', related_name='ronda_de_partido')
    maxjugadores = models.PositiveIntegerField(default = 0)
    quienjuega = models.PositiveIntegerField(default=1)  # indica quien va a jugar
    cantidad_cartas = models.PositiveIntegerField(default=0)  # indica cuantas cartas  se tiraron
    estado = models.PositiveIntegerField(default=PRIMERA_VUELTA)  # 1 2 3 indica las suborndas
    quien_es_mano = models.PositiveIntegerField( default=1 )
    vuelta1 = models.IntegerField(default=-1) # quien gano cada subronda
    vuelta2 = models.IntegerField(default=-1)
    vuelta3 = models.IntegerField(default=-1)


    def hacer_jugar(self, jugador, id_carta):
        envido = self.envido_de_ronda.all()[0]
        truco = self.truco_de_ronda.all()[0]
         # si el jugador numero tal tiene que jugar
         # NO se puede jugar si se esta esperando un quiero
        if self.quienjuega == jugador.get_numero_jugador()\
           and truco.estado != ESPERANDO and envido.estado_envido != ESPERANDO\
           and id_carta != "":
            jugo = jugador.jugar_carta(id_carta, self.estado)
            if jugo: # si efectivamente se jugo
                envido.mensaje = ""
                envido.save()
                self.cantidad_cartas += 1  # tiramos una carta
                self.avanzar()
                self.save()

    def avanzar(self):
        if self.cantidad_cartas % self.maxjugadores == 0:  # significa que podemos actualziar, ya han jugado todo los jugadores
            estado = self.estado
            self.actualizar_vuelta()
            self.actualizar_puntajes()
            self.estado += 1
        else:  # sino podemos actualizar puntajes, entonces
            self.quienjuega += 1
            if self.quienjuega == self.maxjugadores + 1:
                self.quienjuega = 1
        self.save()


    def encontrar_ganador(self):
        cartas = self.cartas_de_la_ronda.filter(tirada_en_vuelta = self.estado)
        minimo = cartas.aggregate(Min('power'))['power__min'] # obtenemos la carta mas poderosa
        cartas = self.cartas_de_la_ronda.filter(tirada_en_vuelta = self.estado, power = minimo)
        ganador = cartas[0].get_jugador().get_numero_equipo()
        winner = cartas[0].get_jugador().get_numero_jugador()
        if len(cartas)>1:
            for i in cartas:
                if ganador != i.get_jugador().get_numero_equipo():
                    ganador = 0
                    break
        return ganador , winner

    def actualizar_vuelta(self):
        ganador, winner = self.encontrar_ganador()
        if self.estado == PRIMERA_VUELTA:
            self.vuelta1 = ganador
        if self.estado == SEGUNDA_VUELTA:
            self.vuelta2 = ganador
        if self.estado == TERCERA_VUELTA:
            self.vuelta3 = ganador
        if ganador != 0:
            self.quienjuega = winner
        else:
            self.quienjuega +=1
            if self.quienjuega == self.maxjugadores + 1:
                self.quienjuega = 1
        self.save()
        return ganador

    def buscar_puntaje(self, valor, palo):
        result = 0
        cero_uno = palo[0] == palo[1]
        cero_dos = palo[0] == palo[2]
        uno_dos = palo[1] == palo[2]

        if not cero_uno and not cero_dos and not uno_dos:
            result = max(valor)
        elif cero_uno and not cero_dos:
            result = 20 + valor[0] + valor [1]
        elif cero_dos and not cero_uno:
            result = 20 + valor[0] + valor [2]
        elif uno_dos and not cero_uno:
            result = 20 + valor[1] + valor[2]
        else: # todos del mimo palo
            comb = []
            comb.append(valor[0] + valor[1])
            comb.append(valor[0] + valor[2])
            comb.append(valor[1] + valor[2])
            result = 20 + max(comb)
        return result

#    def computar_envido(self, partido):
#        envido = self.envido_de_ronda.all()[0]
#        puntos_envido = envido.get_puntos()
#        equipo_ganador_envido = envido.get_ganador()
#        if envido.mostrar_puntos == True: # quiere decir que no se ha solicitado que se muestren los puntos
#            if equipo_ganador_envido != NINGUNO:
#                if equipo_ganador_envido == EQUIPO1:
#                    partido.puntaje1 += puntos_envido
#                elif equipo_ganador_envido == EQUIPO2:
#                    partido.puntaje2 += puntos_envido
#        else: # para dos jugadores dsp rehacer para varios
#            equipos = partido.equipos.all()
#            jugadores_eq1 = equipos[0].jugadores_del_equipo.all()[0]
#            jugadores_eq2 = equipos[1].jugadores_del_equipo.all()[0]
#            cartas_eq1 = jugadores_eq1.cartas.all()
#            cartas_eq2 = jugadores_eq2.cartas.all()
#            valor_eq1 = []
#            palo_eq1 = []
#            valor_eq2 = []
#            palo_eq2 = []
#            for i in range(0,3):
#                palo_eq1.append(cartas_eq1[i].palo)
#                if cartas_eq1[i].valor not in CARTAS_NEGRAS:
#                    valor_eq1.append(cartas_eq1[i].valor)
#                else:
#                    valor_eq1.append(0)
#                palo_eq2.append(cartas_eq2[i].palo)
#                if cartas_eq2[i].valor not in CARTAS_NEGRAS:
#                    valor_eq2.append(cartas_eq2[i].valor)
#                else:
#                    valor_eq2.append(0)
#            puntos_eq1 = self.buscar_puntaje(valor_eq1, palo_eq1)
#            puntos_eq2 = self.buscar_puntaje(valor_eq2, palo_eq2)
#            if puntos_eq1 > puntos_eq2:
#                partido.puntaje1 += puntos_envido
#            elif puntos_eq1 < puntos_eq2:
#                partido.puntaje2 += puntos_envido
#            else: # gana la mano
#                equipo_mano = self.quien_es_mano
#                if equipo_mano == EQUIPO1:
#                    partido.puntaje1 += puntos_envido
#                else:
#                    partido.puntaje2 += puntos_envido

    def computar_envido(self, partido):
        envido = self.envido_de_ronda.all()[0]
        puntos_envido = envido.get_puntos()
        equipo_ganador_envido = envido.get_ganador()
        if envido.mostrar_puntos == True: # quiere decir que no se ha solicitado que se muestren los puntos
            if equipo_ganador_envido != NINGUNO:
                if equipo_ganador_envido == EQUIPO1:
                    partido.puntaje1 += puntos_envido
                elif equipo_ganador_envido == EQUIPO2:
                    partido.puntaje2 += puntos_envido
        else: # para dos jugadores dsp rehacer para varios
            equipos = partido.equipos.all()
            jugadores_eq1 = equipos[0].jugadores_del_equipo.all()
            jugadores_eq2 = equipos[1].jugadores_del_equipo.all()

            puntos_eq1 = 0
            puntos_eq2 = 0
            for k in range(0,len(jugadores_eq1)):
                cartas_eq1 = jugadores_eq1[k].cartas.all()
                cartas_eq2 = jugadores_eq2[k].cartas.all()
                valor_eq1 = []
                palo_eq1 = []
                valor_eq2 = []
                palo_eq2 = []
                for i in range(0,3):
                    palo_eq1.append(cartas_eq1[i].palo)
                    if cartas_eq1[i].valor not in CARTAS_NEGRAS:
                        valor_eq1.append(cartas_eq1[i].valor)
                    else:
                        valor_eq1.append(0)
                    palo_eq2.append(cartas_eq2[i].palo)
                    if cartas_eq2[i].valor not in CARTAS_NEGRAS:
                        valor_eq2.append(cartas_eq2[i].valor)
                    else:
                        valor_eq2.append(0)
                puntos_eq1 = max(self.buscar_puntaje(valor_eq1, palo_eq1), puntos_eq1)
                puntos_eq2 = max(self.buscar_puntaje(valor_eq2, palo_eq2), puntos_eq2)

            if puntos_eq1 > puntos_eq2:
                partido.puntaje1 += puntos_envido
            elif puntos_eq1 < puntos_eq2:
                partido.puntaje2 += puntos_envido
            else: # gana la mano
                equipo_mano = self.quien_es_mano
                if equipo_mano == EQUIPO1:
                    partido.puntaje1 += puntos_envido
                else:
                    partido.puntaje2 += puntos_envido

    def actualizar_puntajes(self):
        partido = self.partido
        partido.ronda_muerta = True
        truco = self.truco_de_ronda.all()[0]
        puntos = truco.get_puntos_truco()

        envido = self.envido_de_ronda.all()[0]
        puntos_envido = envido.get_puntos()
        equipo_ganador_envido = envido.get_ganador()

        # habia una forma mas facil de escribir esto, estoy totalmente seguro de eso... fran p.
        if self.vuelta1 == EQUIPO1 and self.vuelta2 == EQUIPO1 or \
           self.vuelta1 == EQUIPO1 and self.vuelta3 == EQUIPO1 or \
           self.vuelta2 == EQUIPO1 and self.vuelta3 == EQUIPO1:
            partido.puntaje1 += puntos
            self.computar_envido(partido)

        elif self.vuelta1 == EQUIPO2 and self.vuelta2 == EQUIPO2 or \
             self.vuelta1 == EQUIPO2 and self.vuelta3 == EQUIPO2 or \
             self.vuelta2 == EQUIPO2 and self.vuelta3 == EQUIPO2:
            partido.puntaje2 += puntos
            self.computar_envido(partido)

        # pardas en segunda
        elif self.vuelta1 == EQUIPO1 and self.vuelta2 == PARDAS:
            partido.puntaje1 += puntos
            self.computar_envido(partido)

        elif self.vuelta1 == EQUIPO2 and self.vuelta2 == PARDAS:
            partido.puntaje2 += puntos

            self.computar_envido(partido)
        #tripe parda
        elif self.vuelta1 == PARDAS and self.vuelta2 == PARDAS and self.vuelta3==PARDAS:
            if self.quien_es_mano==EQUIPO1:
                partido.puntaje1 += puntos
            else:
                partido.puntaje2 += puntos
            self.computar_envido(partido)

        #doble parda
        elif self.vuelta1 == PARDAS and self.vuelta2 == PARDAS:
            if self.vuelta3 == EQUIPO1:
                partido.puntaje1 += puntos
                self.computar_envido(partido)

            elif self.vuelta3 == EQUIPO2:
                partido.puntaje2 += puntos
                self.computar_envido(partido)

            else:
                partido.ronda_muerta = False
                partido.save()

        #pardas en primera vuelta
        elif self.vuelta1 == PARDAS:
            if self.vuelta2 == EQUIPO1:
                partido.puntaje1 += puntos
                self.computar_envido(partido)
            elif self.vuelta2 == EQUIPO2:
                partido.puntaje2 += puntos
                self.computar_envido(partido)
            else:
                partido.ronda_muerta = False

        else:
            partido.ronda_muerta = False

        # Truco no querido
        if truco.estado ==ME_VOY_AL_MAZO:
            if truco.quien_canto == EQUIPO1:
                partido.puntaje2 += puntos
            elif truco.quien_canto == EQUIPO2:
                partido.puntaje1 += puntos
            partido.ronda_muerta = True
            self.computar_envido(partido)

        if truco.estado == RECHAZADO:
            if truco.quien_canto == EQUIPO1:
                partido.puntaje1 += puntos
            elif truco.quien_canto == EQUIPO2:
                partido.puntaje2 += puntos
            partido.ronda_muerta = True
            self.computar_envido(partido)
        self.save()
        partido.save()

    def cantar_truco(self, numero_equipo, accion):
        truco = self.truco_de_ronda.all()[0]
        puede = truco.puede_cantar_truco(numero_equipo)
        if puede:
            envido = self.envido_de_ronda.all()[0]
            envido.mensaje=""
            envido.save()
            truco.procesar_input(numero_equipo, accion)
            self.actualizar_puntajes()

    def cantar_envido(self, numero_equipo, numero_jugador, accion, puntos_para_falta, puntos):
        envido = self.envido_de_ronda.all()
        envido = envido[0]
        puede = envido.puede_cantar(numero_equipo)
#        print puede
        if puede:
            valido = envido.verificar_input(accion)
#            print valido
            if valido:
                envido.procesar_input(accion, numero_equipo, numero_jugador, puntos_para_falta, puntos)
#                print "Puntos a jugar: ",envido.get_puntos()
#                print "puntos equipo 1: ", envido.puntaje_mentiroso1
#                print "puntos equipo 2: ", envido.puntaje_mentiroso2
#                print "equipo ganador: ", envido.equipo_ganador


    def crear_truco_envido(self):
        envido = Envido(ronda=self, cantidad_jugadores = self.maxjugadores, jugador_a_cantar = self.quienjuega)
#        envido = Envido(ronda=self, cantidad_jugadores = self.maxjugadores)
        envido.save()
        truco = Truco(ronda=self)
        truco.save()

    def botones_truco(self,numero_equipo,numero_jugador):
        truco = self.truco_de_ronda.all()
        truco = truco[0]
        return truco.mostrar_boton_truco(numero_equipo,numero_jugador)

    def botones_envido(self,numero_equipo,numero_jugador):
        envido = self.envido_de_ronda.all()
        envido = envido[0]
        return envido.mostrar_boton_envido(numero_equipo, numero_jugador)
