from django.test import TestCase
from django.contrib.auth.models import User
from truco.models import Carta, Jugador, Ronda, Partido, Equipo, Truco, Envido
from truco.models.constant import *

class TestLogicaInicial(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='nico', email='nico@gmail.com', password='123')
        self.user2 = User.objects.create_user(username='fran', email='fran@gmail.com', password='123')
        self.partido = Partido.objects.create(nombre="hola", ide = 1, maxpuntos = 15, maxjugadores = 2)
        self.partido.unir_jugador(self.user1)
        self.partido.unir_jugador(self.user2)
        self.jugador1 = Jugador.objects.get(usuario = self.user1)
        self.jugador2 = Jugador.objects.get(usuario = self.user2)

    def test_prueba_inicial(self):
        self.assertNotEqual(self.jugador1, self.jugador2)
        equipos = self.partido.equipos.all()
        self.assertEqual(2,len(equipos))
        jugadores_eq1 = equipos[0].jugadores_del_equipo.all()
        jugadores_eq2 = equipos[1].jugadores_del_equipo.all()
        self.assertEqual(1,len(jugadores_eq1))
        self.assertEqual(1,len(jugadores_eq2))
        self.assertTrue(equipos[0].esta_lleno())
        self.assertTrue(equipos[1].esta_lleno())
        self.assertFalse(self.partido.esta_esperando())
        self.assertEqual(self.jugador1.numero,1)
        self.assertEqual(self.jugador2.numero,2)

    def test_empezar_pequenas_partida(self):
        self.partido.demonio_de_partido()
        rondas = self.partido.ronda_de_partido.all()
        ronda = rondas[0]
        self.assertEqual(1, len(rondas))
        self.assertEqual(1, rondas[0].estado)
        self.assertEqual(1, self.partido.numero_ronda)
        self.assertEqual(2, rondas[0].quienjuega)
        self.assertEqual(2, rondas[0].quien_es_mano)
        #obtenemos las cartas
        cartas1 = self.jugador1.cartas.all()
        cartas2 = self.jugador2.cartas.all()
        self.assertEqual(3,len(cartas1))
        self.assertEqual(3,len(cartas2))
        #juega el jugador 2
        self.assertEqual(0,ronda.cantidad_cartas)
        ronda.hacer_jugar(self.jugador2,cartas2[0].ide)
        #vemos que la cantidad de cartas jugadas es 1
        self.assertEqual(1,ronda.cantidad_cartas)
        #juega el 2
        ronda.hacer_jugar(self.jugador1, cartas1[0].ide)
        cartas1 = self.jugador1.cartas.filter(jugada = False)
        cartas2 = self.jugador2.cartas.filter(jugada = False)
        self.assertEqual(2,len(cartas1))
        self.assertEqual(2,len(cartas2))
        card1 = self.jugador1.cartas.filter(jugada = True, tirada_en_vuelta = 1)[0]
        card2 = self.jugador2.cartas.filter(jugada = True,tirada_en_vuelta = 1)[0]
        if card1.power < card2.power:
            self.assertEqual(1,ronda.vuelta1)
            self.assertEqual(1,ronda.quienjuega)
        elif card1.power > card2.power:
            self.assertEqual(2,ronda.vuelta1)
            self.assertEqual(2,ronda.quienjuega)
        else:
            self.assertEqual(0, ronda.vuelta1)
            self.assertEqual(1,ronda.quienjuega)
        #veamos la vuelta 2
        cartas1 = self.jugador1.cartas.filter(jugada = False)
        cartas2 = self.jugador2.cartas.filter(jugada = False)
        self.assertEqual(2,len(cartas1))
        self.assertEqual(2,len(cartas2))
        self.assertEqual(ronda.estado,2)
        #se supone que no cambia
        self.assertEqual(2,ronda.quien_es_mano)
        if ronda.quienjuega == 2:
            ronda.hacer_jugar(self.jugador2, cartas2[0].ide)
            ronda.hacer_jugar(self.jugador1, cartas1[0].ide)
        else:
            ronda.hacer_jugar(self.jugador1, cartas1[0].ide)
            ronda.hacer_jugar(self.jugador2, cartas2[0].ide)
        card1 = self.jugador1.cartas.filter(jugada = True, tirada_en_vuelta = 2)[0]
        card2 = self.jugador2.cartas.filter(jugada = True,tirada_en_vuelta = 2)[0]
        if card1.power < card2.power:
            self.assertEqual(1,ronda.vuelta2)
            self.assertEqual(1,ronda.quienjuega)
        elif card1.power > card2.power:
            self.assertEqual(2,ronda.vuelta2)
            self.assertEqual(2,ronda.quienjuega)
        else:
            self.assertEqual(0, ronda.vuelta2)
            # self.assertEqual(2,ronda.quienjuega)

    def test_partido_terminado(self):
        self.partido.puntaje1 = 14
        self.partido.puntaje2 = 14
        self.partido.demonio_de_partido()
        rondas = self.partido.ronda_de_partido.all()
        ronda = rondas[0]
        self.partido.manejar_truco(self.user1, '')
        self.partido.manejar_truco(self.user2, 'noquiero')
        self.assertTrue(self.partido.ronda_muerta)
        self.partido.demonio_de_partido()
        self.assertEqual(True,self.partido.terminado)



class TestLogicapPuntaje(TestCase):

    def setUp(self):
        self.partido = Partido.objects.create(nombre="hola", ide = 1, maxpuntos = 15, maxjugadores = 2)
        self.partido.save()
        self.ronda = Ronda(partido=self.partido, maxjugadores = 2 ,quienjuega=1 ,quien_es_mano=1)
        self.ronda.save()
        self.ronda.crear_truco_envido()
        self.ronda.save()

    #TESTEAMOS CALCULADOR DE PUNTOS
    def test_caso1(self):
        self.partido.puntaje1 = 0
        self.partido.puntaje2 = 0
        self.ronda.vuelta1 = EQUIPO1
        self.ronda.vuelta2 = EQUIPO2
        self.ronda.vuelta3 = EQUIPO1
        self.ronda.save()
        self.ronda.actualizar_puntajes()
        self.assertEqual(True, self.partido.ronda_muerta)
        self.assertEqual(0,self.partido.puntaje2)
        self.assertEqual(1,self.partido.puntaje1)

    def test_caso2(self):
        self.ronda.vuelta1 = EQUIPO2
        self.ronda.vuelta2 = EQUIPO2
        self.ronda.save()
        self.ronda.actualizar_puntajes()
        self.assertEqual(1,self.partido.puntaje2)
        self.assertEqual(0,self.partido.puntaje1)
        self.assertEqual(True, self.partido.ronda_muerta)


    def test_caso3(self):
        self.ronda.vuelta1 = -1
        self.ronda.vuelta2 = -1
        self.ronda.vuelta3 = -1
        self.ronda.save()
        self.ronda.actualizar_puntajes()
        self.assertEqual(0,self.partido.puntaje2)
        self.assertEqual(0,self.partido.puntaje1)
        self.assertEqual(False, self.partido.ronda_muerta)

    def test_caso4(self):
        self.ronda.vuelta1 = EQUIPO1
        self.ronda.vuelta2 = -1
        self.ronda.vuelta3 = -1
        self.ronda.save()
        self.ronda.actualizar_puntajes()
        self.assertEqual(0,self.partido.puntaje2)
        self.assertEqual(0,self.partido.puntaje1)
        self.assertEqual(False, self.partido.ronda_muerta)

    def test_caso5(self):
        self.ronda.vuelta1 = EQUIPO1
        self.ronda.vuelta2 = EQUIPO2
        self.ronda.vuelta3 = -1
        self.ronda.save()
        self.ronda.actualizar_puntajes()
        self.assertEqual(0,self.partido.puntaje2)
        self.assertEqual(0,self.partido.puntaje1)
        self.assertEqual(False, self.partido.ronda_muerta)

    def test_caso6(self):
        self.ronda.vuelta1 = NINGUNO
        self.ronda.vuelta2 = NINGUNO
        self.ronda.vuelta3 = NINGUNO
        self.ronda.save()
        self.ronda.actualizar_puntajes()
        self.assertEqual(0,self.partido.puntaje2)
        self.assertEqual(1,self.partido.puntaje1)
        self.assertEqual(True, self.partido.ronda_muerta)

    def test_caso7(self):
        self.ronda.vuelta1 = NINGUNO
        self.ronda.vuelta2 = NINGUNO
        self.ronda.vuelta3 = EQUIPO1
        self.ronda.save()
        self.ronda.actualizar_puntajes()
        self.assertEqual(0,self.partido.puntaje2)
        self.assertEqual(1,self.partido.puntaje1)
        self.assertEqual(True, self.partido.ronda_muerta)

    def test_caso8(self):
        # ninguno a jugado
        self.ronda.vuelta1 = NINGUNO
        self.ronda.vuelta2 = EQUIPO1
        self.ronda.vuelta3 = -1
        self.ronda.save()
        self.ronda.actualizar_puntajes()
        self.assertEqual(0,self.partido.puntaje2)
        self.assertEqual(1,self.partido.puntaje1)
        self.assertEqual(True, self.partido.ronda_muerta)

    def test_caso9(self):
        # ninguno a jugado
        self.ronda.vuelta1 = NINGUNO
        self.ronda.vuelta2 = -1
        self.ronda.vuelta3 = -1
        self.ronda.save()
        self.ronda.actualizar_puntajes()
        self.assertEqual(0,self.partido.puntaje2)
        self.assertEqual(0,self.partido.puntaje1)
        self.assertEqual(False, self.partido.ronda_muerta)

    def test_caso10(self):
        # ninguno a jugado
        self.ronda.vuelta1 = EQUIPO1
        self.ronda.vuelta2 = PARDAS
        self.ronda.vuelta3 = -1
        self.ronda.save()
        self.ronda.actualizar_puntajes()
        self.assertEqual(0,self.partido.puntaje2)
        self.assertEqual(1,self.partido.puntaje1)
        self.assertEqual(True, self.partido.ronda_muerta)

    def test_caso11(self):
        # ninguno a jugado
        self.ronda.vuelta1 = EQUIPO2
        self.ronda.vuelta2 = PARDAS
        self.ronda.vuelta3 = -1
        self.ronda.save()
        self.ronda.actualizar_puntajes()
        self.assertEqual(1,self.partido.puntaje2)
        self.assertEqual(0,self.partido.puntaje1)
        self.assertEqual(True, self.partido.ronda_muerta)

class TestComparacionCartas(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='tumama', email='nico@gmail.com', password='123')
        self.user2 = User.objects.create_user(username='fran', email='fran@gmail.com', password='123')
        self.partido = Partido.objects.create(nombre="hola", ide = 1, maxpuntos = 15, maxjugadores = 2)
        self.partido.unir_jugador(self.user1)
        self.partido.unir_jugador(self.user2)
        self.jugador1 = Jugador.objects.get(usuario = self.user1)
        self.jugador2 = Jugador.objects.get(usuario = self.user2)
        self.ronda = Ronda(partido=self.partido, maxjugadores = 2 ,quienjuega=1 ,quien_es_mano=1)
        self.ronda.save()
        self.ronda.crear_truco_envido()
        self.ronda.save()
        self.jugador1.recibir_cartas(self.ronda,18,12,1)
        self.jugador2.recibir_cartas(self.ronda,0,3,35)
        # 18 -- 1 DE ESPADA
        # 0 -- 1 DE BASTO
        # 3 -- 4 DE BASTO
        # 12 --4 DE COPA
        # 2 -- 3 DE BASTO
        # 35 --12 DE ORO


    def test_caso_ganador1(self):
        self.jugador1.jugar_carta(18,1)
        self.jugador2.jugar_carta(0,1)

        ganador = self.ronda.encontrar_ganador()
        self.assertEqual((1,1),ganador)
        # self.assertEqual(1,jugador)



    def test_caso_ganador_pardas(self):
        self.jugador1.jugar_carta(12,1)
        self.jugador2.jugar_carta(3,1)
        ganador = self.ronda.encontrar_ganador()
        self.assertEqual(0,ganador[0])
        #NO NOS INTERESA EL GANADOR


class TestTruco(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='tumama', email='nico@gmail.com', password='123')
        self.user2 = User.objects.create_user(username='fran', email='fran@gmail.com', password='123')
        self.partido = Partido.objects.create(nombre="hola", ide = 1, maxpuntos = 15, maxjugadores = 2)
        self.partido.unir_jugador(self.user1)
        self.partido.unir_jugador(self.user2)
        self.jugador1 = Jugador.objects.get(usuario = self.user1)
        self.jugador2 = Jugador.objects.get(usuario = self.user2)
        self.partido.nueva_ronda()
        self.ronda = self.partido.ronda_de_partido.all()[0]
        self.jugador1.recibir_cartas(self.ronda,18,12,1)
        self.jugador2.recibir_cartas(self.ronda,0,3,35)
        # 18 -- 1 DE ESPADA
        # 0 -- 1 DE BASTO
        # 3 -- 4 DE BASTO
        # 12 --4 DE COPA
        # 2 -- 3 DE BASTO
        # 35 --12 DE ORO


    def test_truco_estados(self):
        ronda = self.partido.ronda_de_partido.all()[0]
        self.assertEqual(1, self.partido.numero_ronda)

        self.partido.manejar_truco(self.user1, '')
        ronda = self.partido.ronda_de_partido.all()[0]
        truco = ronda.truco_de_ronda.all()[0]
        self.assertEqual(NADA, truco.nivel)
        self.assertEqual(TRUCO, truco.siguiente_nivel)
        self.assertEqual(self.jugador1.numero, truco.quien_canto)
        self.assertEqual(ESPERANDO, truco.estado)

        # -----------TRUCO QUIERO-------------#
        self.partido.manejar_truco(self.user2, 'quiero')
        ronda = self.partido.ronda_de_partido.all()[0]
        truco = ronda.truco_de_ronda.all()[0]
        self.assertEqual(TRUCO, truco.nivel)
        self.assertEqual(TRUCO, truco.siguiente_nivel)
        self.assertEqual(self.jugador1.numero, truco.quien_canto)
        self.assertEqual(ACEPTADO, truco.estado)

        # -----------RETRUCO -------------#
        self.partido.manejar_truco(self.user2, 'retruco')
        ronda = self.partido.ronda_de_partido.all()[0]
        truco = ronda.truco_de_ronda.all()[0]
        self.assertEqual(TRUCO, truco.nivel)
        self.assertEqual(RETRUCO, truco.siguiente_nivel)
        self.assertEqual(self.jugador2.numero, truco.quien_canto)
        self.assertEqual(ESPERANDO, truco.estado)

        # -----------RETRUCO QUIERO -------------#
        self.partido.manejar_truco(self.user1, 'quiero')
        ronda = self.partido.ronda_de_partido.all()[0]
        truco = ronda.truco_de_ronda.all()[0]
        self.assertEqual(RETRUCO, truco.nivel)
        self.assertEqual(RETRUCO, truco.siguiente_nivel)
        self.assertEqual(self.jugador2.numero, truco.quien_canto)
        self.assertEqual(ACEPTADO, truco.estado)

        # -----------VALE CUATRO -------------#
        self.partido.manejar_truco(self.user1, 'vale_cuatro')
        ronda = self.partido.ronda_de_partido.all()[0]
        truco = ronda.truco_de_ronda.all()[0]
        self.assertEqual(RETRUCO, truco.nivel)
        self.assertEqual(VALE_CUATRO, truco.siguiente_nivel)
        self.assertEqual(self.jugador1.numero, truco.quien_canto)
        self.assertEqual(ESPERANDO, truco.estado)

        # -----------VALE CUATRO QUIERO -------------#
        self.partido.manejar_truco(self.user2, 'quiero')
        ronda = self.partido.ronda_de_partido.all()[0]
        truco = ronda.truco_de_ronda.all()[0]
        self.assertEqual(VALE_CUATRO, truco.nivel)
        self.assertEqual(VALE_CUATRO, truco.siguiente_nivel)
        self.assertEqual(self.jugador1.numero, truco.quien_canto)
        self.assertEqual(ACEPTADO, truco.estado)


    def test_truco_noquiero(self):
        self.partido.manejar_truco(self.user1, '')
        self.partido.manejar_truco(self.user2, 'noquiero')

        self.assertTrue(self.partido.ronda_muerta)
        self.partido.demonio_de_partido()
        self.assertEqual(1, self.partido.puntaje1)

    def test_retruco_noquiero(self):
        self.partido.manejar_truco(self.user1, '')
        self.partido.manejar_truco(self.user2, 'quiero')
        self.partido.manejar_truco(self.user2, 'retruco')
        self.partido.manejar_truco(self.user1, 'noquiero')

        self.assertTrue(self.partido.ronda_muerta)
        self.partido.demonio_de_partido()
        self.assertEqual(2, self.partido.puntaje2)

    def test_vale4_noquiero(self):
        self.partido.manejar_truco(self.user1, '')
        self.partido.manejar_truco(self.user2, 'quiero')
        self.partido.manejar_truco(self.user2, 'retruco')
        self.partido.manejar_truco(self.user1, 'quiero')
        self.partido.manejar_truco(self.user1, 'vale_cuatro')
        self.partido.manejar_truco(self.user2, 'noquiero')

        self.assertTrue(self.partido.ronda_muerta)
        self.partido.demonio_de_partido()
        self.assertEqual(3, self.partido.puntaje1)


    def test_truco_quiero(self):
        self.partido.manejar_truco(self.user1, '')
        ronda = self.partido.ronda_de_partido.all()[0]
        truco = ronda.truco_de_ronda.all()[0]
        self.assertEqual(2, ronda.quienjuega)
        self.assertEqual(2, ronda.quien_es_mano)

        # -----------TRUCO QUIERO-------------#
        self.partido.manejar_truco(self.user2, 'quiero')
        ronda = self.partido.ronda_de_partido.all()[0]
        truco = ronda.truco_de_ronda.all()[0]
        self.partido.jugar_partido(self.user1, 1)
        self.partido.jugar_partido(self.user2, 3)
        ronda = self.partido.ronda_de_partido.all()[0]
        # self.assertEqual(ronda.vuelta1, self.jugador1.numero)

        # -----------RETRUCO -------------#
        self.partido.manejar_truco(self.user2, 'retruco')
        ronda = self.partido.ronda_de_partido.all()[0]
        truco = ronda.truco_de_ronda.all()[0]

        # -----------RETRUCO QUIERO -------------#
        self.partido.manejar_truco(self.user1, 'quiero')
        ronda = self.partido.ronda_de_partido.all()[0]
        truco = ronda.truco_de_ronda.all()[0]
        self.partido.jugar_partido(self.user1, 12)
        self.partido.jugar_partido(self.user2, 35)
        ronda = self.partido.ronda_de_partido.all()[0]
        # self.assertEqual(ronda.vuelta2, self.jugador2.numero)

        # -----------VALE CUATRO -------------#
        self.partido.manejar_truco(self.user1, 'vale_cuatro')
        ronda = self.partido.ronda_de_partido.all()[0]
        truco = ronda.truco_de_ronda.all()[0]

        # -----------VALE CUATRO QUIERO -------------#
        self.partido.manejar_truco(self.user2, 'quiero')
        ronda = self.partido.ronda_de_partido.all()[0]
        truco = ronda.truco_de_ronda.all()[0]
        self.partido.jugar_partido(self.user2, 0)
        self.partido.jugar_partido(self.user1, 18)
        ronda = self.partido.ronda_de_partido.all()[0]
        # self.assertEqual(ronda.vuelta3, self.jugador1.numero)

        ronda = self.partido.ronda_de_partido.all()[0]
        # self.assertTrue(self.partido.ronda_muerta)
        # self.assertEqual(3, ronda.estado)

        # ------- Computar ------------- #
        self.partido.demonio_de_partido()
        ronda = self.partido.ronda_de_partido.all()[0]
        # self.assertEqual(1 , ronda.quienjuega)
        # self.assertEqual(1 , ronda.quien_es_mano)
        self.assertEqual(0, self.partido.puntaje2)
        # self.assertEqual(4, self.partido.puntaje1)
        # self.assertEqual(2, self.partido.numero_ronda)


class TestUnirJugadores(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='nico', email='nico@gmail.com', password='123')
        self.user2 = User.objects.create_user(username='fran', email='fran@gmail.com', password='123')
        self.user3 = User.objects.create_user(username='maxi', email='maxi@gmail.com', password='123')
        self.user4 = User.objects.create_user(username='ale', email='ale@gmail.com', password='123')
        self.user5 = User.objects.create_user(username='manu', email='manu@gmail.com', password='123')
        self.user6 = User.objects.create_user(username='nachh', email='nachh@gmail.com', password='123')

    def test_partido_dos_jugadores(self):
        self.partido = Partido.objects.create(nombre="hola", ide = 1, maxpuntos = 15, maxjugadores = 2)
        self.partido.unir_jugador(self.user1)
        self.partido.unir_jugador(self.user2)
        self.jugador1 = Jugador.objects.get(usuario = self.user1)
        self.jugador2 = Jugador.objects.get(usuario = self.user2)
        self.assertNotEqual(self.jugador1, self.jugador2)
        equipos = self.partido.equipos.all()
        self.assertEqual(2,len(equipos))
        jugadores_eq1 = equipos[0].jugadores_del_equipo.all()
        jugadores_eq2 = equipos[1].jugadores_del_equipo.all()
        self.assertEqual(1,len(jugadores_eq1))
        self.assertEqual(1,len(jugadores_eq2))
        self.assertTrue(equipos[0].esta_lleno())
        self.assertTrue(equipos[1].esta_lleno())
        self.assertFalse(self.partido.esta_esperando())
        self.assertEqual(self.jugador1.numero,1)
        self.assertEqual(self.jugador2.numero,2)

    def test_partido_cuatro_jugadores(self):
        self.partido = Partido.objects.create(nombre="hola", ide = 1, maxpuntos = 15, maxjugadores = 4)
        self.partido.unir_jugador(self.user1)
        self.partido.unir_jugador(self.user2)
        equipos = self.partido.equipos.all()
        self.assertEqual(1,len(equipos))
        self.jugador1 = Jugador.objects.get(usuario = self.user1)
        self.jugador2 = Jugador.objects.get(usuario = self.user2)
        self.assertNotEqual(self.jugador1, self.jugador2)
        self.assertEqual(self.jugador1.numero,1)
        self.assertEqual(self.jugador2.numero,2)
        self.partido.unir_jugador(self.user3)
        equipos = self.partido.equipos.all()
        self.assertEqual(2,len(equipos))
        self.partido.unir_jugador(self.user4)
        self.jugador3 = Jugador.objects.get(usuario = self.user3)
        self.jugador4 = Jugador.objects.get(usuario = self.user4)
        self.assertEqual(self.jugador3.numero,3)
        self.assertEqual(self.jugador4.numero,4)
        equipos = self.partido.equipos.all()
        self.assertTrue(equipos[0].esta_lleno())
        self.assertTrue(equipos[1].esta_lleno())
        jugadores_eq1 = equipos[0].jugadores_del_equipo.all()
        jugadores_eq2 = equipos[1].jugadores_del_equipo.all()
        self.assertEqual(2,len(jugadores_eq1))
        self.assertEqual(2,len(jugadores_eq2))

    def test_partido_seis_jugadores(self):
        self.partido = Partido.objects.create(nombre="hola", ide = 1, maxpuntos = 15, maxjugadores = 6)
        self.partido.unir_jugador(self.user1)
        self.partido.unir_jugador(self.user2)
        equipos = self.partido.equipos.all()
        self.assertEqual(1,len(equipos))
        self.jugador1 = Jugador.objects.get(usuario = self.user1)
        self.jugador2 = Jugador.objects.get(usuario = self.user2)
        self.assertNotEqual(self.jugador1, self.jugador2)
        self.assertEqual(self.jugador1.numero,1)
        self.assertEqual(self.jugador2.numero,2)
        self.partido.unir_jugador(self.user3)
        equipos = self.partido.equipos.all()
        self.assertEqual(1,len(equipos))
        self.partido.unir_jugador(self.user4)
        self.jugador3 = Jugador.objects.get(usuario = self.user3)
        self.jugador4 = Jugador.objects.get(usuario = self.user4)
        self.assertEqual(self.jugador3.numero,3)
        self.assertEqual(self.jugador4.numero,4)
        equipos = self.partido.equipos.all()
        self.assertEqual(2,len(equipos))
        jugadores_eq1 = equipos[0].jugadores_del_equipo.all()
        jugadores_eq2 = equipos[1].jugadores_del_equipo.all()
        self.assertEqual(3,len(jugadores_eq1))
        self.assertEqual(1,len(jugadores_eq2))
        self.partido.unir_jugador(self.user5)
        self.partido.unir_jugador(self.user6)
        self.jugador5 = Jugador.objects.get(usuario = self.user5)
        self.jugador6 = Jugador.objects.get(usuario = self.user6)
        self.assertEqual(self.jugador5.numero,5)
        self.assertEqual(self.jugador6.numero,6)
        equipos = self.partido.equipos.all()
        self.assertTrue(equipos[0].esta_lleno())
        self.assertTrue(equipos[1].esta_lleno())
        jugadores_eq1 = equipos[0].jugadores_del_equipo.all()
        jugadores_eq2 = equipos[1].jugadores_del_equipo.all()
        self.assertEqual(3,len(jugadores_eq1))
        self.assertEqual(3,len(jugadores_eq2))


class TestVariosPartidos(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='tumama', email='nico@gmail.com', password='123')
        self.user2 = User.objects.create_user(username='fran', email='fran@gmail.com', password='123')
        self.user3 = User.objects.create_user(username='maxi', email='maxi@gmail.com', password='123')
        self.user4 = User.objects.create_user(username='ale', email='ale@gmail.com', password='123')
        self.partido1 = Partido.objects.create(nombre="p1", ide = 1, maxpuntos = 15, maxjugadores = 2)
        self.partido2 = Partido.objects.create(nombre="p2", ide = 2, maxpuntos = 15, maxjugadores = 2)
        self.partido1.unir_jugador(self.user1)
        self.partido1.unir_jugador(self.user2)
        self.partido2.unir_jugador(self.user3)
        self.partido2.unir_jugador(self.user4)
        self.jugador1 = Jugador.objects.get(usuario = self.user1)
        self.jugador2 = Jugador.objects.get(usuario = self.user2)
        self.jugador3 = Jugador.objects.get(usuario = self.user3)
        self.jugador4 = Jugador.objects.get(usuario = self.user4)
        self.partido1.nueva_ronda()
        self.partido2.nueva_ronda()


    def test_una_subronda_cartas_sin_repetir(self):
        ronda1 = self.partido1.ronda_de_partido.all()[0]
        ronda2 = self.partido2.ronda_de_partido.all()[0]
        self.jugador1.recibir_cartas(ronda1,18,12,1)
        self.jugador2.recibir_cartas(ronda1,0,3,35)
        # 18 -- 1 DE ESPADA
        # 12 -- 4 DE COPA
        # 1  -- 2 DE BASTO
        # 0  -- 1 DE BASTO
        # 3  -- 4 DE BASTO
        # 35 -- 12 DE ORO

        self.jugador3.recibir_cartas(ronda2,18,4,6)
        self.jugador4.recibir_cartas(ronda2,2,9,32)
        # 18 -- 1 DE ESPADA
        # 4  -- 5 DE BASTO
        # 6  -- 7 DE BASTO
        # 2  -- 3 DE BASTO
        # 9  -- 1 DE COPA
        # 32 -- 6 DE ORO

        # ----------- INIT -------------#
        self.assertEqual(2, ronda1.quienjuega)
        self.assertEqual(2, ronda2.quienjuega)
        self.assertEqual(2, ronda1.quien_es_mano)
        self.assertEqual(2, ronda2.quien_es_mano)

        # ----------- P1 -------------#
        self.partido1.jugar_partido(self.user2, 3)
        self.partido1.jugar_partido(self.user1, 1)
        ronda1 = self.partido1.ronda_de_partido.all()[0]
        self.assertEqual(ronda1.vuelta1, self.jugador1.numero)

        # ----------- P2 -------------#
        self.partido2.jugar_partido(self.user4, 2)
        self.partido2.jugar_partido(self.user3, 4)
        ronda2 = self.partido2.ronda_de_partido.all()[0]
        self.assertEqual(ronda2.vuelta1, self.jugador4.numero)

    def test_una_subronda_cartas_repetidas(self):
        ronda1 = self.partido1.ronda_de_partido.all()[0]
        ronda2 = self.partido2.ronda_de_partido.all()[0]
        self.jugador1.recibir_cartas(ronda1,18,12,1)
        self.jugador2.recibir_cartas(ronda1,0,3,35)
        # 18 -- 1 DE ESPADA
        # 12 -- 4 DE COPA
        # 1  -- 2 DE BASTO
        # 0  -- 1 DE BASTO
        # 3  -- 4 DE BASTO
        # 35 -- 12 DE ORO

        self.jugador3.recibir_cartas(ronda2,18,12,1)
        self.jugador4.recibir_cartas(ronda2,0,3,35)
        # 18 -- 1 DE ESPADA
        # 12 -- 4 DE COPA
        # 1  -- 2 DE BASTO
        # 0  -- 1 DE BASTO
        # 3  -- 4 DE BASTO
        # 35 -- 12 DE ORO

        # ----------- INIT -------------#
        self.assertEqual(2, ronda1.quienjuega)
        self.assertEqual(2, ronda2.quienjuega)
        self.assertEqual(2, ronda1.quien_es_mano)
        self.assertEqual(2, ronda2.quien_es_mano)

        # ----------- P1 -------------#
        self.partido1.jugar_partido(self.user2, 3)
        self.partido1.jugar_partido(self.user1, 1)
        ronda1 = self.partido1.ronda_de_partido.all()[0]
        self.assertEqual(ronda1.vuelta1, self.jugador1.numero)

        # ----------- P2 -------------#
        self.partido2.jugar_partido(self.user4, 3)
        self.partido2.jugar_partido(self.user3, 1)
        ronda2 = self.partido2.ronda_de_partido.all()[0]
        self.assertEqual(ronda2.vuelta1, self.jugador3.numero)
