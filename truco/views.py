from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from forms import SignUpForm, PartidoForm
from django.contrib.auth.decorators import login_required
from models import Jugador, Partido, Ronda, Carta, Estadistica, Usuario
import time
from django.db.models import Min, Max


def main(request):
    estadistica = Estadistica(ide=0)
    estadistica.save()

    return render_to_response('main.html', {}, context_instance=RequestContext(request))


def abandonar(request, ide):
    partido = Partido.objects.get(ide=ide)
    jugador = Jugador.objects.get(usuario=request.user)
    jugadores = partido.cantidad_jugadores
    partido.abandonar(jugador)

    if jugadores == 1:
        partido.delete()
    jugador.delete()
    return HttpResponseRedirect('lobby')


def signup(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = SignUpForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass

            # Process the data in form.cleaned_data
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            email = form.cleaned_data["email"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]

            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            usuario = Usuario(usuario=user)
            usuario.save()

            return HttpResponseRedirect(reverse('lobby'))  # Redirect after POST
    else:
        form = SignUpForm()

    data = {
        'form': form,
    }
    return render_to_response('signup.html', data, context_instance=RequestContext(request))


def logout(request):
    return HttpResponseRedirect(reverse('login'))


@login_required()
def lobby(request):
    lista_partidos = Partido.objects.filter(esperando=True)
    data = {
        'partidos': lista_partidos,
        'user': request.user,
    }
    return render_to_response('lobby.html', data, context_instance=RequestContext(request))

def aquemesaloco(partido):
    if partido.maxjugadores == 2:
        return 'mesa.html','/mesa'
    elif partido.maxjugadores == 4:
        return 'mesados.html','/mesa'
    else:
        return 'mesatres.html','/mesa'

@login_required()
def mesa(request, ide):
    user = request.user
    partido = Partido.objects.get(ide=ide)
    partido.demonio_de_partido()
    data = partido.obtener_datos_del_partido(user)
    html , path = aquemesaloco(partido)
    return render_to_response( html, data, context_instance=RequestContext(request))

def estadistica(request):

    estadistica = Estadistica.objects.get(ide=0)
    data = estadistica.datos()
    return render_to_response( 'estadistica.html', data, context_instance=RequestContext(request))

@login_required
def jugando(request, ide , carta):
    user = request.user
    partido = Partido.objects.get(ide =ide )
    partido.jugar_partido(user, carta)
    html , path = aquemesaloco(partido)
    return HttpResponseRedirect( path + ide)


@login_required()
def envido(request, ide, opcion = "", puntos = -1): # valores por default
    user = request.user
    partido = Partido.objects.get(ide =ide)
    jugador = Jugador.objects.get(usuario=user)
    ronda = partido.ronda_de_partido.all()[0]

    # Solo se canta envido en la primera subronda
    if ronda.estado == 1:
        partido.manejar_envido(user, opcion, puntos)

    return HttpResponseRedirect('/mesa' + ide)


@login_required()
def truco(request, ide, opcion=""):
    user = request.user
    partido = Partido.objects.get(ide=ide)

    partido.manejar_truco(user, opcion)
    return HttpResponseRedirect('/mesa' + ide)


@login_required()
def crearpartido(request):
    # import ipdb
    # ipdb.set_trace()
    if request.method == 'POST':  # If the form has been submitted...
        form = PartidoForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            user = request.user

            nombre = form.cleaned_data["Nombre"]
            puntaje = form.cleaned_data["Puntaje"]
            cant = form.cleaned_data["Cantidad_Jugadores"]
            partido = Partido( nombre=nombre, maxpuntos=puntaje,maxjugadores = cant)
            partido.save()
            partido.unir_jugador(user)
            return HttpResponseRedirect('mesa' + str(partido.ide))
    else:
        form = PartidoForm()
    data = {
        'form': form,
    }
    return render_to_response('crearpartido.html', data, context_instance=RequestContext(request))


@login_required()
def unirse(request, ide ):
    if request.method == 'GET':
        user = request.user
        partido = Partido.objects.get(ide = ide )
        partido.unir_jugador(user)
        partido.save()
        partido.reacomodar_jugadores()
        html , path = aquemesaloco(partido)

        return HttpResponseRedirect(path + ide)
