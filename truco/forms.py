from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from models import Partido  
from random import randrange


class SignUpForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
        widgets = {
            'password': forms.PasswordInput(),
        }

class PartidoForm(forms.Form):
	Nombre = forms.CharField(max_length=50,help_text='Ingrese un nombre que no contenga espacios.', initial="randname"+str(randrange(500)))
   	Puntaje = forms.ChoiceField(widget=forms.RadioSelect,choices=[(15,'15'),(30,'30')], initial=15)
   	# Puntaje = forms.ChoiceField(widget=forms.RadioSelect,choices=[(3,'15'),(30,'30')], initial=3)
   	Cantidad_Jugadores = forms.ChoiceField(widget = forms.RadioSelect,choices=[(2,'2'),(4,'4'),(6,'6')],initial=2)


