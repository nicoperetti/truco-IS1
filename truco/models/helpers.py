from django.contrib.auth.models import User
from django.db.models import Max

from truco.models.Ronda import Ronda
from truco.models.Equipo import Equipo
from truco.models.Jugador import Jugador

from.constant import *


#--------------- PARTIDO ----------------# 
def obtener_datos_jugador(self, user):
    jugador = Jugador.objects.get(usuario=user)
    numero = jugador.get_numero_jugador()
    nombre = jugador.usuario.get_username()
    cartas = jugador.cartas.filter(jugada=False)
    cartas_jugadas = jugador.cartas.filter(jugada=True)
    return {'jugador':jugador,'cartas1':cartas,'cartas_jugadas1':cartas_jugadas,'ide':str(self.ide),'numero_p':numero}

def obtener_datos_de_jugadores(self , user):
    jugador5="";cartas5="";cartas_jugadas5="";
    jugador6="";cartas6="";cartas_jugadas6="";
    nombre4="";nombre5="";

    jugadores = self.obtener_todo_jugadores()
    if len(jugadores)==2 and self.maxjugadores==2:
        for i in jugadores:
            if i.usuario !=  user:
                jugador = i
        cartas = jugador.cartas.filter(jugada=False)
        cartas_jugadas = jugador.cartas.filter(jugada=True)
        return {'jugador2':jugador,'cartas2':cartas,'cartas_jugadas2':cartas_jugadas}
    elif len(jugadores)>=4 and self.maxjugadores>=4:
        for i in jugadores:
            if i.get_numero_jugador()==1:
                jugador1=i
                nombre1= jugador1.usuario.username
                cartas1 = jugador1.cartas.filter(jugada=False)
                assert len(cartas1)>0
                cartas_jugadas1 = jugador1.cartas.filter(jugada=True)
            elif i.get_numero_jugador()==2:
                jugador2=i
                nombre2= jugador2.usuario.username
                cartas2 = jugador2.cartas.filter(jugada=False)
                assert len(cartas2)>0
                cartas_jugadas2 = jugador2.cartas.filter(jugada=True)
            elif i.get_numero_jugador()==3:
                jugador3=i
                nombre3= jugador3.usuario.username
                cartas3 = jugador3.cartas.filter(jugada=False)
                assert len(cartas3)>0
                cartas_jugadas3 = jugador3.cartas.filter(jugada=True)
            elif i.get_numero_jugador()==4:
                jugador4=i
                nombre4= jugador4.usuario.username

                cartas4 = jugador4.cartas.filter(jugada=False)
                assert len(cartas4)>0
                print(cartas4)
                cartas_jugadas4 = jugador4.cartas.filter(jugada=True)
                print "hola como ca >>>>>>>>>>>>>>>>>><"
            elif i.get_numero_jugador()==5:
                jugador5=i
                nombre5= jugador5.usuario.username
                cartas5 = jugador5.cartas.filter(jugada=False)
                assert len(cartas5)>0
                cartas_jugadas5 = jugador5.cartas.filter(jugada=True)
            elif i.get_numero_jugador()==6:
                jugador6=i
                nombre6= jugador6.usuario.username
                cartas6 = jugador6.cartas.filter(jugada=False)
                assert len(cartas6)>0
                cartas_jugadas6 = jugador6.cartas.filter(jugada=True)
        return{ 'jugador1':jugador1,'cartas1':cartas1,'cartas_jugadas1':cartas_jugadas1,
                'jugador2':jugador2,'cartas2':cartas2,'cartas_jugadas2':cartas_jugadas2,
                'jugador3':jugador3,'cartas3':cartas3,'cartas_jugadas3':cartas_jugadas3,
                'jugador4':jugador4,'cartas4':cartas4,'cartas_jugadas4':cartas_jugadas4,
                'jugador5':jugador5,'cartas5':cartas5,'cartas_jugadas5':cartas_jugadas5,
                'jugador6':jugador6,'cartas6':cartas6,'cartas_jugadas6':cartas_jugadas6}

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
        res = ronda.botones_envido(jugador.get_numero_equipo(),jugador.get_numero_jugador())
        data = dict(data.items() + res.items())
        res = self.obtener_datos_jugador(user)
        data = dict(data.items() + res.items())
        print_estado = self.print_estado(user, data)
        try:
            res = self.obtener_datos_de_jugadores(user)
            data = dict(data.items() + res.items()) #obtenemos los datos de otro jugador
            envido = ronda.envido_de_ronda.all()[0]
            envido_cantado = envido.get_estado_envido()
        except Exception:
            pass
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
    truco = ronda.truco_de_ronda.all()[0]
    if nequipo == 1:
        puntos_tuyos = self.puntaje1
        puntos_otro = self.puntaje2
    elif nequipo == 2:
        puntos_tuyos = self.puntaje2
        puntos_otro = self.puntaje1

    if truco.estado == ESPERANDO and truco.quien_canto != nequipo:
        if truco.siguiente_nivel == TRUCO and truco.nivel == NADA:
            return "Te cantaron truco"
        elif truco.siguiente_nivel == RETRUCO and truco.nivel == TRUCO:
            return "Te cantaron retruco"
        elif truco.siguiente_nivel == VALE_CUATRO and truco.nivel == RETRUCO:
            return "Te cantaron vale cuatro"

    elif truco.estado == ESPERANDO and truco.quien_canto == nequipo:
        return "Esperando respuesta"

    elif self.terminado and puntos_tuyos > puntos_otro:
        return "Ganaste! Tus puntos: " + str(puntos_tuyos)+" "+ "Los del otro: "+str(puntos_otro)

    elif self.terminado and puntos_tuyos < puntos_otro:
        return "Te hicieron de goma! Tus puntos: " + str(puntos_tuyos)+" "+ "Los del otro: "+str(puntos_otro)

    elif self.terminado and puntos_tuyos == puntos_otro:
        return "Empate!"
    else:
    	return ""
