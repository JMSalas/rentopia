from django.db import models
from django.contrib.auth.models import User
from django.contrib import messages

# Create your models here.
class Region(models.Model):
    nombre = models.CharField(max_length=60, null=False)

    def __str__(self):
        return self.nombre
    
    
class Comuna(models.Model):
    nombre = models.CharField(max_length=50, null=False)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class Direccion(models.Model):
    calle = models.CharField(max_length=50, null=False)
    numero = models.IntegerField(blank=True, null=True)
    dpto = models.CharField(max_length=5, blank=True, null=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE, null=False)

    def existe_en_db(self,request):
        #Retorna instancia del modelo, ya sea recuperada o recién creada 
        direccion, created = Direccion.objects.get_or_create(
            calle=self.calle,
            numero=self.numero,
            dpto=self.dpto,
            comuna=self.comuna
        )

        if created:
            messages.success(request, "Direccion: Se asigno una nueva direccion")
        else:
            messages.success(request, "Direccion: Se asigno una direccion existente")

        return direccion
    
    def asociada_en_db(self, user):
        #Verifica si instancia de una direccion esta asociada a otros user o a una propiedad
        asociada_a_propiedad = Propiedad.objects.filter(direccion=self).first()
        asociada_a_profiles = Profile.objects.filter(direccion=self).exclude(user=user).first()

        return asociada_a_propiedad or asociada_a_profiles

    def __str__(self):
        str = f'{self.calle} {self.numero}'

        if self.dpto:
            str += f' {self.dpto}'
        
        str += f', {self.comuna}, {self.comuna.region}.'

        return str

class TipoUsuario(models.Model):
    nombre = models.CharField(max_length=20, null=False)

    def __str__(self):
        return self.nombre


class Profile(models.Model):
    rut = models.CharField(max_length=9, unique=True)
    telefono = models.CharField(max_length=9, null=False)
    tipo = models.ForeignKey(TipoUsuario, on_delete=models.PROTECT, null=False, default=1)
    direccion = models.ForeignKey(Direccion, on_delete=models.PROTECT, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.rut


class TipoPropiedad(models.Model):
    nombre = models.CharField(max_length=20, null=False)

    def __str__(self):
        return self.nombre
    

class Propiedad(models.Model):
    nombre = models.CharField(max_length=50, null=False)
    descripcion = models.CharField(max_length=500, null=False)
    m2_construidos = models.FloatField(null=False)
    m2_totales = models.FloatField(null=False)
    estacionamientos = models.SmallIntegerField(null=False)
    habitaciones = models.SmallIntegerField(null=False)
    banos = models.SmallIntegerField(null=False)
    precio_arriendo = models.IntegerField(null=False)
    meses_garantia = models.SmallIntegerField(null=False)
    disponible = models.BooleanField(default=False)
    fecha_publicacion = models.DateField(auto_now_add=True)
    fecha_modificacion = models.DateField(auto_now=True)
    google_map = models.URLField(null=False)
    tipo_propiedad = models.ForeignKey(TipoPropiedad, on_delete=models.PROTECT)
    arrendador = models.ForeignKey(Profile, on_delete=models.CASCADE)
    direccion = models.OneToOneField(Direccion, on_delete=models.CASCADE)
    interesados = models.ManyToManyField(Profile, through='SolicitudArriendo', related_name='propiedades')

    def get_thumb_image(self):
        thumb = self.imagen_set.filter(foto__iendswith='thumb.png').first()
        if not thumb:
            thumb = self.imagen_set.filter(foto__iendswith='thumb.jpeg').first()
        return thumb
    
    def __str__(self):
        return f'{self.nombre} - {self.direccion}'


class Estado(models.Model):
    nombre = models.CharField(max_length=15, null=False)

    def __str__(self):
        return self.nombre


class SolicitudArriendo(models.Model):
    fecha_solicitud = models.DateField(auto_now_add=True)
    fecha_revision = models.DateField(null=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, default=1,null=False)
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE)
    arrendatario = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f"Nº Solicitud: {self.id}, Propiedad: {self.propiedad}, Solicitante: {self.arrendatario}, Estado: {self.estado}"

def image_upload_path(instance, filename):
    # Get the pk of the associated Propiedad
    propiedad_pk = instance.propiedad.pk if instance.propiedad else 'new'
    
    # Generate the path
    return f'propiedad/{propiedad_pk}/{filename}'

class Imagen(models.Model):
    foto = models.ImageField(upload_to=image_upload_path)
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE)

    class Meta:

        verbose_name = 'Imagen'
        verbose_name_plural = 'Imagenes'

    def __str__(self):
        return self.foto.name
