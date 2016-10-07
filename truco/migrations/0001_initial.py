# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Carta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ide', models.PositiveIntegerField()),
                ('palo', models.PositiveIntegerField()),
                ('valor', models.PositiveIntegerField()),
                ('power', models.PositiveIntegerField()),
                ('jugada', models.BooleanField(default=False)),
                ('tirada_en_vuelta', models.PositiveIntegerField(default=0)),
                ('imagen', models.CharField(max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Envido',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nivel_envido', models.PositiveIntegerField(default=0)),
                ('nivel_old', models.PositiveIntegerField(default=0)),
                ('estado_envido', models.IntegerField(default=-1)),
                ('quien_canto', models.PositiveIntegerField(default=0)),
                ('puntaje_mentiroso1', models.PositiveIntegerField(default=-1)),
                ('puntaje_mentiroso2', models.PositiveIntegerField(default=-1)),
                ('equipo_ganador', models.PositiveIntegerField(default=0)),
                ('mostrar_puntos', models.BooleanField(default=True)),
                ('cantidad_jugadores', models.PositiveIntegerField(default=2)),
                ('jug_cataron', models.PositiveIntegerField(default=0)),
                ('jugador_a_cantar', models.PositiveIntegerField(default=1)),
                ('mensaje', models.CharField(default=b'', max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Equipo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero', models.IntegerField(default=1)),
                ('cantidad_jugadores', models.IntegerField(default=0)),
                ('total_de_jugadores', models.IntegerField(default=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Estadistica',
            fields=[
                ('ide', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Jugador',
            fields=[
                ('usuario', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('numero', models.PositiveIntegerField(default=0)),
                ('puntos_cantados', models.IntegerField(default=-1)),
                ('equipo', models.ForeignKey(related_name=b'jugadores_del_equipo', to='truco.Equipo')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Partido',
            fields=[
                ('ide', models.AutoField(serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=50)),
                ('esperando', models.BooleanField(default=True)),
                ('puntaje1', models.PositiveIntegerField(default=0)),
                ('puntaje2', models.PositiveIntegerField(default=0)),
                ('numero_ronda', models.PositiveIntegerField(default=0)),
                ('terminado', models.BooleanField(default=False)),
                ('maxpuntos', models.PositiveIntegerField(default=5)),
                ('cantidad_jugadores', models.PositiveIntegerField(default=0)),
                ('maxjugadores', models.PositiveIntegerField(default=0)),
                ('ronda_muerta', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ronda',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('maxjugadores', models.PositiveIntegerField(default=0)),
                ('quienjuega', models.PositiveIntegerField(default=1)),
                ('cantidad_cartas', models.PositiveIntegerField(default=0)),
                ('estado', models.PositiveIntegerField(default=1)),
                ('quien_es_mano', models.PositiveIntegerField(default=1)),
                ('vuelta1', models.IntegerField(default=-1)),
                ('vuelta2', models.IntegerField(default=-1)),
                ('vuelta3', models.IntegerField(default=-1)),
                ('partido', models.ForeignKey(related_name=b'ronda_de_partido', to='truco.Partido')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Truco',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nivel', models.PositiveIntegerField(default=1)),
                ('siguiente_nivel', models.PositiveIntegerField(default=1)),
                ('quien_canto', models.PositiveIntegerField(default=0)),
                ('estado', models.IntegerField(default=-1)),
                ('ronda', models.ForeignKey(related_name=b'truco_de_ronda', to='truco.Ronda')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('usuario', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('cantidad_partidas_ganadas', models.IntegerField(default=0)),
                ('estadistica', models.ForeignKey(related_name=b'estadistica_user', to='truco.Estadistica')),
                ('partido', models.ForeignKey(related_name=b'usuarios', to='truco.Partido')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='equipo',
            name='partido',
            field=models.ForeignKey(related_name=b'equipos', to='truco.Partido'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='envido',
            name='ronda',
            field=models.ForeignKey(related_name=b'envido_de_ronda', to='truco.Ronda'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='carta',
            name='jugador',
            field=models.ForeignKey(related_name=b'cartas', to='truco.Jugador'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='carta',
            name='ronda',
            field=models.ForeignKey(related_name=b'cartas_de_la_ronda', to='truco.Ronda'),
            preserve_default=True,
        ),
    ]
