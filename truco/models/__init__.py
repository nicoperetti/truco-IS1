# En cada model se debe agregar subclase:
#    class Meta:
#        app_label = "truco"

# Aca en init las clases se importan en orden:
#    if classA tiene ForeignKey(classB) then
#       importar primero classB

from truco.models.Partido import Partido
from truco.models.Ronda import Ronda
from truco.models.Equipo import Equipo
from truco.models.Jugador import Jugador
from truco.models.Envido import Envido
from truco.models.Truco import Truco
from truco.models.Carta import Carta
from truco.models.Usuario import Usuario
from truco.models.Estadistica import Estadistica
