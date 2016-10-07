# fuente de inspiracion:
# http://www.nomadjourney.com/2009/11/splitting-up-django-models/

import sys

VALID_ARGS = ["-d", "-g"]
FOREIGN_KEYS = 0
USES_OBJECTS = 1


if len(sys.argv) != 2 or sys.argv[1] not in VALID_ARGS:
    print "python script.py [OPCION] < [ARCHIVO CON MODELS]"
    print "\t-d\tSolo chequea dependencias entre models (ForeignKey + instanciacion de objetos)."
    print "\t-g\tGenera models separados y chequea dependencias."
    sys.exit()


# Todos los models. Para ir chequeando dependencias
# Si aparece un model que no esta en esta lista, salta un assert.
models = ["Partido", "Ronda", "Equipo", "Jugador", "Envido", "Truco", "Carta"]

# Diccionario con dependencias
deps = {}
for m in models:
    deps[m] = [[], []]

# Leo input hasta que aparezca primer "class"
for line in sys.stdin:
    if "class" in line:
        break

# Abro archivo para primer model
words = line.split(" ")
filename = words[1].split("(")
assert(filename[0] in models)
if sys.argv[1] == "-g":
    f = open(filename[0]+".py", "w")
    f.write(line)

# Sigo leyendo hasta el dofon
for line in sys.stdin:

    # Chequeo dependencias.
    if "class" not in line:
        for m in models:
            # primero de ForeignKey
            if "ForeignKey" in line and m in line and m != filename[0]:
                deps[filename[0]][FOREIGN_KEYS].append(m)
            # luego de objetos
            if "ForeignKey" not in line and m in line and m != filename[0]:
                deps[filename[0]][USES_OBJECTS].append(m)

    # Si aparece nuevo model, creo archivo.
    if "class" in line:
        words = line.split(" ")
        filename = words[1].split("(")
        assert(filename[0] in models)
        if sys.argv[1] == "-g":
            f.close()
            f = open(filename[0]+".py", "w")

    # Voy escribiendo en el archivo del model actual
    if sys.argv[1] == "-g":
        f.write(line)

if sys.argv[1] == "-g":
    f.close()


# Genero __init__.py
# Hay que reordenar a mano:
#    if classA tiene ForeignKey(classB) then
#       importar primero classB
if sys.argv[1] == "-g":
    f = open("__init__.py", "w")
    for m in models:
        line = "from truco.models." + m + " import " + m + "\n"
        f.write(line)
    f.close()

# Muestro por stdout las dependencias
# list(set(L)) borra duplicados de L
for model in models:
    assert(len(deps[model]) == 2)
    # primero de ForeignKey
    string = model + "\tFKs:\t"
    for uses in list(set(deps[model][FOREIGN_KEYS])):
        string = string + uses + ", "
    print string
    # luego de objetos
    string = "\tobj:\t"
    for uses in list(set(deps[model][USES_OBJECTS])):
        string = string + uses + ", "
    print string
