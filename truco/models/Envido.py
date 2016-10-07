from django.db import models

from.constant import *


class Envido(models.Model):
    class Meta:
        app_label = "truco"

    ronda = models.ForeignKey('Ronda', related_name='envido_de_ronda')
    nivel_envido =  models.PositiveIntegerField( default = SIN_ENVIDO )
    nivel_old = models.PositiveIntegerField( default = SIN_ENVIDO )
    estado_envido = models.IntegerField( default = INICIAL)
    quien_canto = models.PositiveIntegerField( default = NINGUNO)
    puntaje_mentiroso1 = models.PositiveIntegerField( default = -1) # equipo 1
    puntaje_mentiroso2 = models.PositiveIntegerField( default = -1) # equipo 2
    equipo_ganador = models.PositiveIntegerField( default = NINGUNO)
    mostrar_puntos = models.BooleanField(default=True)

    cantidad_jugadores = models.PositiveIntegerField( default = 2)
    jug_cataron = models.PositiveIntegerField( default = 0)

    jugador_a_cantar = models.PositiveIntegerField( default = 1)
    mensaje = models.CharField(default="",max_length=100)


    def get_estado_envido(self):
        return self.estado_envido

    def get_ganador(self):
        return self.equipo_ganador

    def verificar_input(self, accion): # verificamos que lo que se va a cantar se pueda cantar y no cantemos envido con el realenvido ya cantado
        result = False
        if accion == "quiero" or accion == "noquiero":
            result = self.estado_envido == ESPERANDO
        elif accion == "envido":
            if self.nivel_envido in [SIN_ENVIDO, ENV]:
                result = True
        elif accion == "real_envido":
            if self.nivel_envido in [SIN_ENVIDO, ENV, ENV2]:
                result = True
        elif accion == "falta_envido":
            result = True
        elif accion == "" and self.estado_envido == ACEPTADO: # cante puntos
            result = True
        elif accion == "son_buenas":
            if self.estado_envido == ACEPTADO:
                result = True
        elif accion == "mostrar_puntos":
            if self.estado_envido == CALCULADO:
                result = True
        else:
            print "estas mal loco, accion no posible"
            result = False
        return result

    def puede_cantar(self, numero_equipo):
        result = False
        if self.estado_envido == INICIAL:
            result = True
        elif self.estado_envido == ESPERANDO and self.quien_canto != numero_equipo:
            result = True
        elif self.estado_envido == ACEPTADO or self.estado_envido == CALCULADO:
            result = True
        return result

    def procesar_input(self, accion, numero_equipo, numero_jugador, puntos_para_falta, puntos):
        self.quien_canto = numero_equipo
        if accion == "quiero":
            self.estado_envido = ACEPTADO
        elif accion == "noquiero":
            self.estado_envido = RECHAZADO
            self.nivel_envido = self.nivel_old
            if numero_equipo == EQUIPO1:
                self.equipo_ganador = EQUIPO2
            else:
                self.equipo_ganador = EQUIPO1
        elif accion == "envido":
            self.nivel_old = self.nivel_envido
            self.estado_envido = ESPERANDO
            if self.nivel_envido == SIN_ENVIDO:
                self.nivel_envido = ENV
            elif self.nivel_envido == ENV:
                self.nivel_envido = ENV2
        elif accion == "real_envido":
            self.estado_envido = ESPERANDO
            self.nivel_old = self.nivel_envido
            if self.nivel_envido == SIN_ENVIDO:
                self.nivel_envido = REAL_ENV
            elif self.nivel_envido == ENV:
                self.nivel_envido = ENV_REAL_ENV
            elif self.nivel_envido == ENV2:
                self.nivel_envido = ENV2_REAL_ENV
        elif accion == "falta_envido":
            self.estado_envido = ESPERANDO
            self.nivel_old = self.nivel_envido
            self.nivel_envido = puntos_para_falta
        elif accion == "": # cantar puntos: muy feo esta escrito esto merjorar jaj
            kk=self.ronda.partido.obtener_todo_jugadores()
            print len(kk),"<<<<<<<<<<<<<<<<<<<"
            jug=0
            for i in kk:
                if i.get_numero_jugador()==numero_jugador:
                    jug = i.usuario.username
            self.mensaje = " Atencion!!  " +jug+" canto "+str(puntos)+" puntos "
            siguiente = (numero_jugador+1)%self.cantidad_jugadores
            if siguiente == 0:
                siguiente = self.cantidad_jugadores
            self.jugador_a_cantar = siguiente
            if numero_equipo == EQUIPO1:
                self.puntaje_mentiroso1 = max(int(self.puntaje_mentiroso1), puntos)
                self.jug_cataron += 1
            if numero_equipo == EQUIPO2:
                self.puntaje_mentiroso2 = max(int(self.puntaje_mentiroso2), puntos)
                self.jug_cataron += 1
            if self.jug_cataron == self.cantidad_jugadores:
                self.estado_envido = CALCULADO
                asd1 = int(self.puntaje_mentiroso1)
                asd2 = int(self.puntaje_mentiroso2)
                if asd1 < asd2:
                    self.equipo_ganador = EQUIPO2
                elif asd1 > asd2:
                    self.equipo_ganador = EQUIPO1
                else: # caso de tener mismos puntos, ver quien es mano
                    ronda = self.ronda
                    self.equipo_ganador = ronda.quien_es_mano # me dice quien es mano en la ronda
        elif accion == "son_buenas": # modificar esto tambien para que se adapte a 4 y 6 jugadores.
            if numero_equipo == EQUIPO1:
                self.equipo_ganador = EQUIPO2
            else:
                self.equipo_ganador = EQUIPO1
        elif accion == "mostrar_puntos":
            self.mostrar_puntos = False
        else:
            print "estas mal loco, accion no posible"
        self.save()

    def get_puntos(self):
        return self.nivel_envido

    def mostrar_boton_envido(self,numero_equipo, numero_jugador):
        ronda = self.ronda
        if ronda.estado > 1:
            return {'envido':False,'realenvido':False,'faltaenvido':False,'boton_quiero_envido':False, 'boton_puntos':False, 'mostrar_puntos': False}
        aux = ronda.quienjuega == numero_jugador
        boton_quiero = self.quien_canto != numero_equipo and self.estado_envido==ESPERANDO
        boton_puntos = self.quien_canto != numero_equipo and self.estado_envido == ACEPTADO
#        print "botones puntos: ",boton_puntos
        if self.cantidad_jugadores in [4,6] and self.estado_envido == ACEPTADO:
            boton_puntos = False
            if self.jugador_a_cantar == numero_jugador:
                boton_puntos = True

        boton_mostrar_puntos = self.estado_envido == CALCULADO and self.mostrar_puntos
        if self.estado_envido == INICIAL and aux:
            result = {'envido':True,'realenvido':True,'faltaenvido':True,'boton_quiero_envido':boton_quiero, 'boton_puntos':False, 'mostrar_puntos': boton_mostrar_puntos}
        elif self.estado_envido == ESPERANDO and self.quien_canto != numero_equipo:
            if self.nivel_envido == SIN_ENVIDO or self.nivel_envido== ENV: # puedo mostrar todos los botones
                result = {'envido':True,'realenvido':True,'faltaenvido':True,'boton_quiero_envido':boton_quiero, 'boton_puntos':False, 'mostrar_puntos': boton_mostrar_puntos}
            elif self.nivel_envido == ENV2:
                result = {'envido':False, 'realenvido':True, 'faltaenvido':True, 'boton_quiero_envido':boton_quiero, 'boton_puntos':False, 'mostrar_puntos': boton_mostrar_puntos}
            elif self.nivel_envido == REAL_ENV or self.nivel_envido==ENV2_REAL_ENV:
                result = {'envido':False, 'realenvido':False, 'faltaenvido':True, 'boton_quiero_envido':boton_quiero, 'boton_puntos':False, 'mostrar_puntos': boton_mostrar_puntos}
            else: # falta envido
                result = {'envido':False,'realenvido':False,'faltaenvido':False,'boton_quiero_envido':boton_quiero, 'boton_puntos':False, 'mostrar_puntos': boton_mostrar_puntos}
        elif self.estado_envido == ACEPTADO:
            result = {'envido':False,'realenvido':False,'faltaenvido':False,'boton_quiero_envido':False, 'boton_puntos':boton_puntos, 'mostrar_puntos': boton_mostrar_puntos}
        else:
            result = {'envido':False,'realenvido':False,'faltaenvido':False,'boton_quiero_envido':boton_quiero, 'boton_puntos':False, 'mostrar_puntos': boton_mostrar_puntos}
        return result
