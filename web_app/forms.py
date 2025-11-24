from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Direccion, Profile, Propiedad, Imagen

class UserForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ('username', 'email','first_name','last_name','password1', 'password2')

        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
        }

class UserEditForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ('username', 'email','first_name','last_name')

        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
        }

class ProfileForm(forms.ModelForm):
    
    class Meta:

        model = Profile
        fields = ('rut','telefono','tipo')

class DireccionForm(forms.ModelForm):
    
    class Meta:

        model = Direccion
        fields = ('calle','numero','dpto','comuna')

class PropiedadForm(forms.ModelForm):

    class Meta:

        model = Propiedad
        exclude = ('arrendador','direccion','interesados')

        labels = {
            'm2_construidos': 'Mts. Cuadrados Construidos',
            'm2_totales': 'Mts. Cuadrados Totales',
            'banos': 'Baños',
            'precio_arriendo' : 'Precio Arriendo',
        }

        widgets = {
            'descripcion': forms.Textarea(attrs={'style': 'width: 100%;'}),
        }

class ImagenForm(forms.ModelForm):

    class Meta:

        model = Imagen
        fields = ('foto',)
