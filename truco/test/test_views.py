# from django.test import TestCase
# from django.contrib.auth.models import User
# from django.test import Client
# from truco.models import Carta, Jugador, Ronda, Partido, Equipo, Truco, Envido
# from truco.constant import *
#
# from test_constants import *
#
#
# class TestViews(TestCase):
#
#     accion = ACCIONES
#
#     def setUp(self):
#         super(TestViews, self).setUp()
#         # Clientes virtuales.
#         self.client1 = Client()
#         self.client2 = Client()
#         # Un usuario esta logueado y listo para jugar un partido
#         User.objects.create_user(username=NAME1, password=PASS)
#         self.client1.login(username=NAME1, password=PASS)
#         self.user1 = User.objects.all()[0]
#         self.client1.post("/crearpartido", {"Nombre": PARTIDO_NAME, "Puntaje": PARTIDO_PUNTOS, "Cantidad_Jugadores": 2})
#         self.assertEqual(1, len(Partido.objects.all()))
#         self.partido = Partido.objects.all()[0]
#         self.assertEqual(1, len(Jugador.objects.all()))
#         self.jugador1 = Jugador.objects.get(usuario=self.user1)
#         # El otro va pasando por todas las views
#         # Caso de uso 1. Registrarse
#         response = self.client2.get("/signup")
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "signup.html")
#         response = self.client2.post("/signup", {"username": NAME2, "password": PASS})
# #        self.client2.login(username=NAME2, password=PASS)
#
#     def test_views_login(self):
#         # Caso de uso 2. Loguearse
#         response = self.client2.get("/login")
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "login.html")
#         response = self.client2.login(username=NAME2, password=PASS)
#         self.assertTemplateUsed(response, "lobby.html")
#
#     def test_views_crear_partido(self):
#         # Caso de uso 3. Crear nueva partido
#         response = self.client2.get("/crearpartido")
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "crearpartido.html")
# #        response = self.client2.post("/crearpartido", {"Nombre": PARTIDO_NAME, "Puntaje": PARTIDO_PUNTOS, "Cantidad_Jugadores": 2})
# #        self.assertTemplateUsed(response, "mesa.html")
#
#     def test_views_unirse(self):
#         # Caso de uso 4. Unirse a una partido
#         response = self.client2.get("/unirse"+str(PARTIDO_IDE))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "mesa.html")
#
#     def test_views_abandonar(self):
#         # Caso de uso 5. Abandonar partida
#         response = self.client2.get("/abandonar"+str(PARTIDO_IDE))
# #        self.assertEqual(response.status_code, 200)
# #        self.assertTemplateUsed(response, "lobby.html")
#
#
#
# #    def test_list(self):
# #        res = self.client.get(reverse('bbtt:list'))
# #        self.assertEqual(res.status_code, 200)
# #        self.assertTemplateUsed(res, 'bbtt/list.html')
# #        self.assertContains(res, "plist")
#
