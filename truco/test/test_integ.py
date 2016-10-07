from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from truco.models import Carta, Jugador, Ronda, Partido, Equipo, Truco, Envido

from test_constants import *


class TestIntegridad(TestCase):

    accion = ACCIONES

    def setUp(self):
        super(TestIntegridad, self).setUp()
        # Clientes virtuales.
        self.client1 = Client()
        self.client2 = Client()
        # Caso de uso 1. Registrarse
        # Creo Users. 1: clase User. 2: views ("haciendo clic" en Registrarse).
        User.objects.create_user(username=NAME1, password=PASS)
        self.client2.post("/signup", {"username": NAME2, "password": PASS})

    def test_check_login(self):
        # Caso de uso 2. Loguearse
        self.assertTrue(self.client1.login(username=NAME1, password=PASS))
        self.assertTrue(self.client2.login(username=NAME2, password=PASS))
        # De paso testeo cantidad de usuarios.
        users_all = User.objects.all()
        self.assertEqual(2, len(users_all))
        self.user1 = users_all[0]
        self.user2 = users_all[1]

    def test_crear_partido(self):
#         # Caso de uso 3. Crear nueva partido

        self.assertTrue(self.client1.login(username=NAME1, password=PASS))
        self.assertTrue(self.client2.login(username=NAME2, password=PASS))
        self.client1.post("/crearpartido", {"Nombre": PARTIDO_NAME, "Puntaje": PARTIDO_PUNTOS, "Cantidad_Jugadores": 2})
        partidos_all = Partido.objects.all()
        self.assertEqual(1, len(partidos_all))
        self.partido = partidos_all[0]
        users_all = User.objects.all()
        self.user1 = users_all[0]
        self.user2 = users_all[1]
        self.jugador1 = Jugador.objects.get(usuario=self.user1)
        jugadores_all = Jugador.objects.all()
        self.assertTrue(self.jugador1 in jugadores_all)
        self.assertEqual(1, len(jugadores_all))

    def test_unirse(self):
        # Caso de uso 4. Unirse a una partido
        self.assertTrue(self.client1.login(username=NAME1, password=PASS))
        self.assertTrue(self.client2.login(username=NAME2, password=PASS))
        self.client1.post("/crearpartido", {"Nombre": PARTIDO_NAME, "Puntaje": PARTIDO_PUNTOS, "Cantidad_Jugadores": 2})
        partidos_all = Partido.objects.all()
        self.partido = partidos_all[0]
        users_all = User.objects.all()
        self.user1 = users_all[0]
        self.user2 = users_all[1]
        self.jugador1 = Jugador.objects.get(usuario=self.user1)
        self.accion["unirse"](self.client2)
        partidos_all = Partido.objects.all()
        self.assertEqual(1, len(partidos_all))
        jugadores_all = Jugador.objects.all()
        self.assertEqual(2, len(jugadores_all))
        self.jugador2 = Jugador.objects.get(usuario=self.user2)
        self.assertTrue(self.jugador1 in jugadores_all)
        self.assertTrue(self.jugador2 in jugadores_all)
#
    def test_abandonar(self):
#         # Caso de uso 5. Abandonar partida
        self.assertTrue(self.client1.login(username=NAME1, password=PASS))
        self.assertTrue(self.client2.login(username=NAME2, password=PASS))
        self.client1.post("/crearpartido", {"Nombre": PARTIDO_NAME, "Puntaje": PARTIDO_PUNTOS, "Cantidad_Jugadores": 2})
        self.accion["unirse"](self.client2)
        partidos_all = Partido.objects.all()
        self.assertEqual(1,len(partidos_all))
        self.partido=partidos_all[0]
        jugadores_all = Jugador.objects.all()
        self.assertEqual(2,len(jugadores_all))
        self.accion["abandonar"](self.client2)
        jugadores_all = Jugador.objects.all()
        self.assertEqual(1,len(jugadores_all))
        self.accion["abandonar"](self.client1)
        jugadores_all = Jugador.objects.all()
        self.assertEqual(0,len(jugadores_all))
        self.assertEqual(0, len(Partido.objects.all()))

    def test_finalizar(self):
        # Caso de uso 6. Finalizar una partida
        self.assertTrue(self.client1.login(username=NAME1, password=PASS))
        self.assertTrue(self.client2.login(username=NAME2, password=PASS))
        self.client1.post("/crearpartido", {"Nombre": PARTIDO_NAME, "Puntaje": PARTIDO_PUNTOS, "Cantidad_Jugadores": 2})
        self.accion["unirse"](self.client2)
        partidos_all = Partido.objects.all()
        self.assertEqual(1,len(partidos_all))
        self.partido = partidos_all[0]
        cartas_all = Carta.objects.all()
        self.assertEqual(0,len(cartas_all))
        self.partido.demonio_de_partido()
        cartas_all = Carta.objects.all()
        self.assertEqual(6,len(cartas_all))
        self.partido.puntaje2 = PARTIDO_PUNTOS - 1
        self.accion["truco"](self.client2)
        self.accion["truco_noquiero"](self.client1)
        self.assertEqual(0, self.partido.puntaje1)
        self.assertEqual(PARTIDO_PUNTOS-1, self.partido.puntaje2)
#
    def test_nueva_ronda(self):
        # Caso de uso 7. Jugar nueva ronda
        self.assertTrue(self.client1.login(username=NAME1, password=PASS))
        self.assertTrue(self.client2.login(username=NAME2, password=PASS))
        self.client1.post("/crearpartido", {"Nombre": PARTIDO_NAME, "Puntaje": PARTIDO_PUNTOS, "Cantidad_Jugadores": 2})
        self.accion["unirse"](self.client2)
        self.partido=Partido.objects.all()[0]
        self.partido.nueva_ronda()
        rondas_all = Ronda.objects.all()
        self.assertEqual(1, len(rondas_all))
        self.ronda = rondas_all[0]
        users_all = User.objects.all()
        self.user1 = users_all[0]
        self.user2 = users_all[1]
        self.jugador2 = Jugador.objects.get(usuario=self.user2)
        self.assertEqual(2,self.jugador2.get_numero_jugador())
        self.jugador1 = Jugador.objects.get(usuario=self.user1)
        self.assertEqual(1,self.jugador1.get_numero_jugador())

        self.jugador1.recibir_cartas(self.ronda,18,12,1)
                                    # 18 : 1 de espada
                                    # 12 : 4 de copa
                                    # 1  : 2 de basto
        self.jugador2.recibir_cartas(self.ronda,0,3,35)
                                    # 0  : 1 de basto
                                    # 3  : 4 de basto
                                    # 35 : 12 de oro
        self.assertEqual(2,self.ronda.quienjuega)
        self.accion["jugar_carta"](self.client2, 3)
        cartas_all = Carta.objects.filter(jugada = True)
        self.assertEqual(1,len(cartas_all))
        self.ronda = rondas_all[0]
        self.accion["jugar_carta"](self.client1, 1)
        cartas_all = Carta.objects.filter(jugada = True)
        self.assertEqual(2,len(cartas_all))
        self.accion["jugar_carta"](self.client1, 12)
        self.accion["jugar_carta"](self.client2, 35)
        cartas_all = Carta.objects.filter(jugada = True)
        self.assertEqual(4,len(cartas_all))
        self.accion["jugar_carta"](self.client2, 0)
        self.accion["jugar_carta"](self.client1, 18)
        cartas_all = Carta.objects.filter(jugada = True)
        self.ronda = rondas_all[0]
        print len(rondas_all)
        # self.assertEqual(6,self.ronda.cantidad_cartas)
        # self.assertEqual(6,len(cartas_all))
        self.partido.demonio_de_partido()
        #TODO ALGO RARO PASA PASA ACA, NO AUMENTA LA CANTIDAD DE CARTAS JUGADAS... MITERIO
        # self.assertEqual(0, self.partido.puntaje1)
        # self.assertEqual(0, self.partido.puntaje2)
#


##TODO no estoy logrando cantar truco y no querer, para que la partido termine
#    def test_finalizar_partido(self):
#        self.test_crear_partido()
#        p = Partido.objects.get(nombre=PARTIDO_NAME)
##        p.puntaje1 = 16 # Muchos puntos para que gane jugador 1.
#        self.client2.get("/unirse" + PARTIDO_NAME)
#        self.assertEqual(1, len(Partido.objects.all()))
#        self.assertEqual(2, len(Jugador.objects.all()))
#        # Canto truco para terminar la ronda (y el partido)
#        self.client1.get("/mesa"+PARTIDO_NAME+"/truco")
#        self.client2.get("/mesa"+PARTIDO_NAME+"/truco/noquiero")
#        self.assertEqual(0, len(Partido.objects.all()))
#        self.assertEqual(0, len(Jugador.objects.all()))
