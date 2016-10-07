BASTO  = 0
COPA   = 1
ESPADA = 2
ORO    = 3

IDE   = 0
VALOR = 1
PALO  = 2
POWER = 3
 
# [ide,valor,palo,power]
CARTAS = [
          [0,1,BASTO,2],
          [1,2,BASTO,6],
          [2,3,BASTO,5],
          [3,4,BASTO,14],
          [4,5,BASTO,13],
          [5,6,BASTO,12],
          [6,7,BASTO,11],
          [7,11,BASTO,9],
          [8,12,BASTO,8],
          [9,1,COPA,7],
          [10,2,COPA,6],
          [11,3,COPA,5],
          [12,4,COPA,14],
          [13,5,COPA,13],
          [14,6,COPA,12],
          [15,7,COPA,11],
          [16,11,COPA,9],
          [17,12,COPA,8],
          [18,1,ESPADA,1],
          [19,2,ESPADA,6],
          [20,3,ESPADA,5],
          [21,4,ESPADA,14],
          [22,5,ESPADA,13],
          [23,6,ESPADA,12],
          [24,7,ESPADA,3],
          [25,11,ESPADA,9],
          [26,12,ESPADA,8],
          [27,1,ORO,7],
          [28,2,ORO,6],
          [29,3,ORO,5],
          [30,4,ORO,14],
          [31,5,ORO,13],
          [32,6,ORO,12],
          [33,7,ORO,4],
          [34,11,ORO,9],
          [35,12,ORO,8],
          # Para jugar con 10 usar rango [0:40]
          [36,10,BASTO,10],
          [37,10,COPA,10],
          [38,10,ESPADA,10],
          [39,10,ORO,10]
         ]

CARTAS_NEGRAS = [10,11,12]


# Para los cantados

# ------PUNTAJES-------#
NADA = 1
TRUCO = 2
RETRUCO = 3
VALE_CUATRO = 4
ME_VOY_AL_MAZO = 5

SIN_ENVIDO = 0
ENV = 2
REAL_ENV = 3
ENV2 = 4
ENV_REAL_ENV = 5
ENV2_REAL_ENV = 7
FALTA_ENVIDO = 10

# ------ESTADOS-------#
INICIAL = -1
ESPERANDO = 0
ACEPTADO = 1
RECHAZADO = 2
CALCULADO = 3

NO_QUIERO = 0
QUIERO = 1

NINGUNO = 0
EQUIPO1 = 1
EQUIPO2 = 2

PRIMERA_VUELTA = 1
SEGUNDA_VUELTA = 2
TERCERA_VUELTA = 3

PARDAS = 0
GANO_UNO = 1
GANO_DOS = 2

