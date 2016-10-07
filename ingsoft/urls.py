from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.conf import settings

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'truco.views.main', name='main'),
    url(r'^signup$', 'truco.views.signup', name='signup'),
    url(r'^login/$', login, {'template_name': 'login.html', }, name="login"),
    url(r'^lobby$', 'truco.views.lobby', name='lobby'),
    url(r'^mesa(?P<ide>\w+)/envido/(?P<opcion>\w+)', 'truco.views.envido', name='jugando'),
    url(r'^mesa(?P<ide>\w+)/cantar/(?P<puntos>\w+)', 'truco.views.envido', name='jugando'),
    url(r'^mesa(?P<ide>\w+)/truco/(?P<opcion>\w+)', 'truco.views.truco', name='jugando'),
    url(r'^mesa(?P<ide>\w+)/truco', 'truco.views.truco', name='jugando'),
    url(r'^mesa(?P<ide>\w+)/(?P<carta>\w+)', 'truco.views.jugando', name='jugando'),
    url(r'^mesa(?P<ide>\w+)$', 'truco.views.mesa', name='mesa'),
    url(r'^logout$', logout, {'template_name': 'main.html', }, name="logout"),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    url(r'^crearpartido$', 'truco.views.crearpartido', name='crearpartido'),
    url(r'^unirse(?P<ide>\w+)$', 'truco.views.unirse'),
    url(r'^estadistica', 'truco.views.estadistica'),
    url(r'^abandonar(?P<ide>\w+)$', 'truco.views.abandonar'),

    # url(r'^home$', 'truco.views.home', name='home'),
)
