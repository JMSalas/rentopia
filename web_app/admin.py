from django.contrib import admin
from .models import Profile,Propiedad,Direccion,TipoUsuario,TipoPropiedad

# Register your models here.
admin.site.register(Profile)
admin.site.register(Propiedad)
admin.site.register(Direccion)
admin.site.register(TipoUsuario)
admin.site.register(TipoPropiedad)
