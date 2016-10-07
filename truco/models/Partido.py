from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max
from random import shuffle

from truco.models.Ronda import Ronda
from truco.models.Equipo import Equipo
from truco.models.Jugador import Jugador
from truco.models.Usuario import Usuario
from.constant import *


class Partido(models.Model):
    class Meta:
        app_label = "truco"

#    Estadistica = models.ForeignKey('Estadistica', related_name='estadistica_de_partido')

    ide = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    esperando = models.BooleanField(default=True)
    puntaje1 = models.PositiveIntegerField(default=0)
    puntaje2 = models.PositiveIntegerField(default=0)
    numero_ronda = models.PositiveIntegerField(default=0)
    terminado = models.BooleanField(default=False)
    maxpuntos = models.PositiveIntegerField(default=5)
    cantidad_jugadores = models.PositiveIntegerField(default = 0) # Cantidad de jugadores en el partido
    maxjugadores = models.PositiveIntegerField(default=0) # Cantidad de jugadores maximo
    ronda_muerta = models.BooleanField(default = True)

    def demonio_de_partido(self):
        self.gano_alguien()
        if self.ronda_muerta and not self.esperando and not self.terminado:
            self.nueva_ronda()
            self.repartir()
        self.save()

    def nueva_ronda(self):
        proximomano = 1
        if self.numero_ronda > 0:
            self.terminar_ronda()
        self.numero_ronda += 1
        self.ronda = Ronda(partido=self, maxjugadores = self.maxjugadores ,quienjuega=self.numero_ronda % self.maxjugadores +1 ,quien_es_mano=(self.numero_ronda % 2) + 1)
        self.ronda.save()
        self.ronda.crear_truco_envido()
        self.ronda_muerta = False
        self.save()

    def repartir(self):
        assert not self.esperando
        assert not self.terminado
        assert not self.ronda_muerta

        cartas = range(0, 36)
        shuffle(cartas)
        shuffle(cartas) # porque somos extremistas
        players = self.obtener_todo_jugadores()
        indice = 0
        for i in players:
            i.recibir_cartas(self.ronda_de_partido.all()[0],cartas[indice],cartas[indice+1],cartas[indice+2])
            indice += 3
        self.repartido = True
        self.save()

    def jugar_partido(self, user, carta):
        jugador = Jugador.objects.get(usuario=user)
        ronda = self.ronda_de_partido.all()[0]
        envido = ronda.envido_de_ronda.all()[0]
        if envido.get_estado_envido() in [INICIAL, CALCULADO,RECHAZADO]:
            ronda.hacer_jugar(jugador, carta)


    def reacomodar_jugadores(self):
        if not self.esperando:
            jugadores = self.obtener_todo_jugadores()
#            print jugadores
            if len(jugadores)==4 or len(jugadores)==6:
                for i in jugadores:
                    if i.get_numero_jugador()==2:
                        jugador2=i
                    if i.get_numero_jugador()==4:
                        jugador4=i
                    if i.get_numero_jugador()==3:
                        jugador3=i
                    if i.get_numero_jugador()==5:
                        jugador5=i
                if len(jugadores)==6:
                    jugador2.numero=5
                    jugador2.save()
                    jugador5.numero=2
                    jugador5.save()
                else:
                    jugador3.numero = 2
                    jugador3.save()
                    jugador2.numero = 3
                    jugador2.save()

    def unir_jugador(self,user):
        if self.esperando:
            equipos = self.equipos.all()
            if len(equipos) == 0 :
                can = int(self.maxjugadores)
                equipo = Equipo(numero=1, cantidad_jugadores=0, total_de_jugadores = (can / 2), partido = self )
                equipo.save()
                equipo.crear_jugador(user,self.cantidad_jugadores + 1 )
                self.cantidad_jugadores += 1
            elif len(equipos) == 1:
                equipo = equipos[0]
                if not equipo.esta_lleno():
                    equipo.crear_jugador(user,self.cantidad_jugadores + 1 )
                    self.cantidad_jugadores += 1
                else:
                    can = int(self.maxjugadores)
                    equipo = Equipo(numero=2, cantidad_jugadores=0, total_de_jugadores = (can / 2), partido = self )
                    equipo.save()
                    equipo.crear_jugador(user,self.cantidad_jugadores + 1 )
                    self.cantidad_jugadores += 1
            elif len(equipos) == 2:
                for i in equipos:
                    if i.get_numero()==2 :
                        dos = i
                if not dos.esta_lleno():
                    dos.crear_jugador(user,self.cantidad_jugadores + 1 )
                    self.cantidad_jugadores += 1
        if self.cantidad_jugadores == self.maxjugadores:
            self.esperando = False
        self.save()

    def abandonar(self, jugador):
        self.terminado = True
        self.cantidad_jugadores -= 1
        self.save()

    def obtener_todo_jugadores(self):
        equipos = self.equipos.all()
        result = []
        for i in equipos:
            aux = i.obtener_jugadores()
            result += aux
        return result

    def levantar_rondas(self, ronda):
        ronda.delete()
        players = self.jugadores.all()  # ahora vamos las cartas de los jugadores
        cartas_muertas = []
        for i in players:
            cartas_muertas += i.cartas.all()  # obtenemos todas las cartas muertas
        for i in cartas_muertas:
            i.delete()  # chau cartas zombies
        self.save()

    def terminar_ronda(self):
        try:
            ronda = self.ronda_de_partido.all()[0]
            # assert ronda.esta_muerta()
            self.levantar_rondas(ronda)
            self.ronda_muerta = True
            self.save()
        except Exception:
            pass

    def gano_alguien(self):
        if self.maxpuntos <= self.puntaje1 or self.maxpuntos<= self.puntaje2:
            self.terminado = True

            equipo_ganador = self.quien_gano()
            equipos = self.equipos.all()
            if equipos[0].numero == equipo_ganador:
                eq = equipos[0]
            else:
                eq = equipos[1]
            jug = eq.jugadores_del_equipo.all()
            for i in jug:
                jug_usuer = i.usuario
                usuar = self.usuarios.filter(usuario = jug_usuer)
                usuar.incrementar()
                usuar.save()
        self.save()

    def quien_gano(self):
        if self.maxpuntos <= self.puntaje1:
            res = 1
        else:
            res = 2
        return res


    def manejar_truco(self, user, accion):
        ronda = self.ronda_de_partido.all()[0]
        numero_equipo = self.jugador_pertenece_equipo(user)
        envido = ronda.envido_de_ronda.all()[0]
        if envido.get_estado_envido() in [INICIAL, CALCULADO,RECHAZADO]:
            ronda.cantar_truco(numero_equipo, accion)

    def jugador_pertenece_equipo(self, user):
        jugador = Jugador.objects.get(usuario=user)
        return jugador.get_numero_equipo()

    def manejar_envido(self, user, accion, puntos): # puntos son los que se cantan pueden ser mentirosos
        numero = self.jugador_pertenece_equipo(user)
        jugador = Jugador.objects.get(usuario=user)
        numero_jugador = jugador.numero
        ronda = self.ronda_de_partido.all()[0]
        puntos_para_falta = self.maxpuntos - max(self.puntaje1, self.puntaje2)
        ronda.cantar_envido(numero, numero_jugador, accion, puntos_para_falta, puntos)
        ronda.save()

    def puntos_jugador(self, equipo):
        if equipo == 1:
            return self.puntaje1
        return self.puntaje2

    def obtener_datos_jugador(self , user):
        ronda = self.ronda_de_partido.all()[0]

        jugador = Jugador.objects.get(usuario=user)
        numero = jugador.get_numero_jugador()
        nombre = jugador.usuario.get_username()
        cartas = jugador.cartas.filter(jugada=False,ronda = ronda)
        cartas_jugadas = jugador.cartas.filter(jugada=True,ronda = ronda)
        return {'jugador':jugador,'cartas1':cartas,'cartas_jugadas1':cartas_jugadas,'ide':str(self.ide),'numero_p':numero}

    def obtener_datos_de_jugadores(self , user):
        ronda = self.ronda_de_partido.all()[0]
        jugador5="";cartas5="";cartas_jugadas5="";
        jugador6="";cartas6="";cartas_jugadas6="";
        nombre4="";nombre5="";
        cartas1="";cartas2="";cartas3="";cartas4="";cartas5="";cartas6=""
        cartas_jugadas1="";cartas_jugadas2="";cartas_jugadas3="";cartas_jugadas4="";
        jugadores = self.obtener_todo_jugadores()
        if len(jugadores)==2 and self.maxjugadores==2:
            for i in jugadores:
                if i.usuario !=  user:
                    jugador = i
            cartas = jugador.cartas.filter(jugada=False,ronda = ronda)
            cartas_jugadas = jugador.cartas.filter(jugada=True,ronda = ronda)
            return {'jugador2':jugador,'cartas2':cartas,'cartas_jugadas2':cartas_jugadas}
        elif len(jugadores)>=4 and self.maxjugadores>=4:
#            print len(jugadores)
            for i in jugadores:
#                print i,i.numero
                if i.get_numero_jugador()==1:
                    jugador1=i
                    nombre1= jugador1.usuario.username
                    cartas1 = jugador1.cartas.filter(jugada=False,ronda = ronda)
                    cartas_jugadas1 = jugador1.cartas.filter(jugada=True)

                elif i.get_numero_jugador()==2:
                    jugador2=i
                    nombre2= jugador2.usuario.username
                    cartas2 = jugador2.cartas.filter(jugada=False,ronda = ronda)
                    cartas_jugadas2 = jugador2.cartas.filter(jugada=True,ronda = ronda)

                elif i.get_numero_jugador()==3:
                    jugador3=i
#                    print jugador3
                    cartas3 = jugador3.cartas.filter(jugada=False,ronda = ronda)
                    cartas_jugadas3 = jugador3.cartas.filter(jugada=True,ronda = ronda)
#                    print cartas3
#                    print cartas_jugadas3
                elif i.get_numero_jugador()==4:
                    jugador4=i
                    nombre4= jugador4.usuario.username
                    cartas4 = jugador4.cartas.filter(jugada=False,ronda = ronda)
#                    print(cartas4)
                    cartas_jugadas4 = jugador4.cartas.filter(jugada=True,ronda = ronda)
#                    print "hola como ca >>>>>>>>>>>>>>>>>><"

                elif i.get_numero_jugador()==5:
                    jugador5=i
                    nombre5= jugador5.usuario.username
                    cartas5 = jugador5.cartas.filter(jugada=False,ronda = ronda)
                    cartas_jugadas5 = jugador5.cartas.filter(jugada=True,ronda = ronda)

                elif i.get_numero_jugador()==6:
                    jugador6=i
                    nombre6= jugador6.usuario.username
                    cartas6 = jugador6.cartas.filter(jugada=False,ronda = ronda)
                    cartas_jugadas6 = jugador6.cartas.filter(jugada=True,ronda = ronda)

            casa={ 'jugador1':jugador1,'cartas1':cartas1,'cartas_jugadas1':cartas_jugadas1,
                'jugador2':jugador2,'cartas2':cartas2,'cartas_jugadas2':cartas_jugadas2,
                'jugador3':jugador3,'cartas3':cartas3,'cartas_jugadas3':cartas_jugadas3,
                'jugador4':jugador4,'cartas4':cartas4,'cartas_jugadas4':cartas_jugadas4,
                'jugador5':jugador5,'cartas5':cartas5,'cartas_jugadas5':cartas_jugadas5,
                'jugador6':jugador6,'cartas6':cartas6,'cartas_jugadas6':cartas_jugadas6}
#            print casa
#            print len(casa)
            return casa

    def esta_esperando(self):
        return self.esperando

    def obtener_datos_del_partido(self, user):
        # vevo
        jugador = Jugador.objects.get(usuario=user)
        ronda = self.ronda_de_partido.all()
        nequipo = jugador.get_numero_equipo()
        jugadores = self.obtener_todo_jugadores()
        nombre1=""
        nombre2=""
        if len(jugadores)>1:
            if jugadores[0].numero ==1 :
                nombre1 = jugadores[0].usuario.get_username()
                nombre2 = jugadores[1].usuario.get_username()
            else:
                nombre2 = jugadores[0].usuario.get_username()
                nombre1 = jugadores[1].usuario.get_username()
        data = {}
        print_estado = ""
        envido_cantado = ""
        if len(ronda) > 0:  # puede ser que el partido no tenga ninguna ronda
            ronda = ronda[0]
            data = ronda.botones_truco(jugador.get_numero_equipo(),jugador.get_numero_jugador())
            print "---------------------------------------------------asd----------------------------------------------"
            res = ronda.botones_envido(jugador.get_numero_equipo(),jugador.get_numero_jugador())
            print "jugador: ", jugador.get_numero_jugador()
            print "equipo: ", jugador.get_numero_equipo()
            print "---------------------------------------------------------------------------", res
            data = dict(data.items() + res.items())
            res = self.obtener_datos_jugador(user)
            data = dict(data.items() + res.items())
            print_estado = self.print_estado(user, data)

            res = self.obtener_datos_de_jugadores(user)
            data = dict(data.items() + res.items()) #obtenemos los datos de otro jugador
            envido = ronda.envido_de_ronda.all()[0]
            envido_cantado = envido.get_estado_envido()

        data = dict(data.items() + {
            'nombre_jugador1':nombre1,
            'nombre_jugador2':nombre2,
            'partido': self,
            'ronda': ronda,
            'ide': self.ide,
            'abandonaron': (self.cantidad_jugadores < self.maxjugadores) and self.terminado and not self.esperando,
            'envido_cantado': envido_cantado,
            'print_estado':print_estado,
            'puntaje1':self.puntaje1,
            'puntaje2':self.puntaje2
        }.items())
        # print data ,"ultimo"
        return data

    def print_estado(self, user, dicc):
        jugador = Jugador.objects.get(usuario=user)
        nequipo = jugador.get_numero_equipo()
        ronda = self.ronda_de_partido.all()[0]
        envido = ronda.envido_de_ronda.all()[0]
        truco = ronda.truco_de_ronda.all()[0]
        if nequipo == 1:
            puntos_tuyos = self.puntaje1
            puntos_otro = self.puntaje2
        elif nequipo == 2:
            puntos_tuyos = self.puntaje2
            puntos_otro = self.puntaje1


        #--------------- TRUCO ----------------#
        if envido.mensaje != "":
            resultado = envido.mensaje
        elif truco.estado == ESPERANDO and truco.quien_canto != nequipo:
            if truco.siguiente_nivel == TRUCO and truco.nivel == NADA:
                resultado = "Te cantaron truco"
            elif truco.siguiente_nivel == RETRUCO and truco.nivel == TRUCO:
                resultado = "Te cantaron retruco"
            elif truco.siguiente_nivel == VALE_CUATRO and truco.nivel == RETRUCO:
                resultado = "Te cantaron vale cuatro"
        elif truco.estado == ACEPTADO and truco.quien_canto == nequipo:
            resultado = "Aceptado"
        elif truco.estado == RECHAZADO and truco.quien_canto == nequipo:
            resultado = "RECHAZADO"
        elif truco.estado == ESPERANDO and truco.quien_canto == nequipo:
            resultado = "Esperando respuesta"

        #--------------- ENVIDO ----------------#
        elif envido.estado_envido == ESPERANDO and envido.quien_canto != nequipo:
            if envido.nivel_envido == ENV and envido.nivel_old == SIN_ENVIDO:
                resultado = "Te cantaron envido"
            elif envido.nivel_envido == ENV2 and envido.nivel_old == ENV:
                resultado = "Te cantaron envido envido"
            elif envido.nivel_envido == REAL_ENV:
                resultado = "Te cantaron real envido"
            else:
                resultado = "Te cantaron falta envido"
        elif envido.estado_envido == ACEPTADO and envido.quien_canto != nequipo:
            resultado = "Aceptado"
        elif envido.estado_envido == RECHAZADO and envido.quien_canto != nequipo:
            resultado = "Rechazado"
        elif envido.estado_envido == ESPERANDO and envido.quien_canto == nequipo:
            resultado = "Esperando respuesta"

        #--------------- PARTIDO ----------------#
        elif self.terminado and puntos_tuyos > puntos_otro:
            resultado = "Ganaste! Tus puntos: " + str(puntos_tuyos)+" "+ "Los del otro: "+str(puntos_otro)
        elif self.terminado and puntos_tuyos < puntos_otro:
            resultado = "Te hicieron de goma! Tus puntos: " + str(puntos_tuyos)+" "+ "Los del otro: "+str(puntos_otro)
        elif self.terminado and puntos_tuyos == puntos_otro:
            resultado = "Empate!"

        else:
            resultado = ""
        return resultado

    def __unicode__(self):
        return self.nombre

#class Estadistica(models.Model):

#    def datos(self):
#        data = {}
#        usuario = self.estadistica_user.all()
##        for i in usuario:
##            data = dict(data.item() + {'i': i.cantidad_partidas_ganadas}.item())
#        data = dict(data.item() + {'usuarios':usuario}.item())
#        return data

#class Usuario(models.Model):

#    usuario = models.OneToOneField(User, primary_key=True)
#    estadistica = models.ForeignKey('Estadistica', related_name='estadistica_user')
#    partido = models.ForeignKey('Partido', related_name='usuarios')
#    cantidad_partidas_ganadas = models.IntegerField(default=0)

#    def incrementar(self):
#        self.cantidad_partidas_ganadas += 1

#    def __unicode__(self):
#        return self.usuario
