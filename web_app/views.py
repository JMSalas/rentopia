import os
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.datastructures import MultiValueDict
from .forms import UserForm, UserEditForm, ProfileForm, DireccionForm, PropiedadForm, ImagenForm
from .models import Propiedad, Profile, Region, Comuna, Imagen
from django.db.utils import IntegrityError
from PIL import Image
from .decorators import arrendador_required


# Create your views here.
def index(request):
    return render(request, 'web_app/index.html')

@login_required
def profile(request):
    return render(request, 'web_app/profile.html')

# def signup_view(request):
#     return render(request, 'web_app/signed_up.html')

@arrendador_required
def properties_list(request):
    propiedades = Propiedad.objects.filter(arrendador=request.user.profile).order_by("direccion__comuna__region", "direccion__comuna")

    return render(request, 'web_app/properties_list.html', {'propiedades': propiedades})

def wip_view(request):
    return render(request, 'web_app/work_in_progress.html')

def create_user(request):
    
    user_form = UserForm(request.POST or None)
    profile_form = ProfileForm(request.POST or None)
    dir_form = DireccionForm(request.POST or None)
    all_errors = None
    
    if request.method == 'POST':        
        if user_form.is_valid() and profile_form.is_valid() and dir_form.is_valid():
            # Procesar forms validos
            user = user_form.save()
            direccion = dir_form.save(commit = False)
            profile = profile_form.save(commit = False)
            
            direccion = direccion.existe_en_db(request)
            
            profile.direccion = direccion
            profile.user = user
            profile.save()
            
            # Redirige a login de usuario
            messages.success(request, "Felicitaciones usuario creado exitosamente. Por favor, intenta ingresar.")
            return redirect('login')  
        
        else:
            # Combinar errores de form
            all_errors = MultiValueDict()
            for form in [user_form, profile_form, dir_form]:
                for field, errors in form.errors.items():
                    all_errors.appendlist(field, errors)
    
    context = {'user_form': user_form, 'profile_form': profile_form, 'dir_form': dir_form, 'all_errors': all_errors}
    
    return render(request, 'web_app/custom_user.html', context)

@login_required
def edit_user(request):
    
    user = request.user
    user_form = UserEditForm(request.POST or None, instance=user)
    profile_form = ProfileForm(request.POST or None, instance=user.profile)
    dir_form = DireccionForm(request.POST or None, instance=user.profile.direccion)
    all_errors = None
    
    if request.method == 'POST':        
        if user_form.is_valid() and profile_form.is_valid() and dir_form.is_valid():
            # Procesar forms validos
            user = user_form.save()
            direccion = dir_form.save(commit = False)
            profile = profile_form.save(commit = False)
            
            direccion_old = user.profile.direccion
            direccion_new = direccion.existe_en_db(request)
            
            profile.direccion = direccion_new
            profile.user = user
            profile.save()

            if not direccion_old.asociada_en_db(user) and direccion_old.pk != direccion_new.pk:
                direccion_old.delete()
                messages.success(request, "Direccion antigua no estaba asociada. Se elimino.")
            
            # Redirige a login de usuario
            messages.success(request, "Actualizacion de datos de usuario exitosa. Por favor, revisa tu informacion.")
            return redirect('profile')  
        
        else:
            # Combinar errores de form
            all_errors = MultiValueDict()
            for form in [user_form, profile_form, dir_form]:
                for field, errors in form.errors.items():
                    all_errors.appendlist(field, errors)
    
    context = {'user_form': user_form, 'profile_form': profile_form, 'dir_form': dir_form, 'all_errors': all_errors}
    
    return render(request, 'web_app/custom_user.html', context)

@arrendador_required
def create_property(request):
    
    propiedad_form = PropiedadForm(request.POST or None)
    dir_form = DireccionForm(request.POST or None)
    all_errors = None
    
    if request.method == 'POST':        
        if propiedad_form.is_valid() and dir_form.is_valid():
            # Procesar forms validos
            direccion = dir_form.save(commit = False)
            propiedad = propiedad_form.save(commit = False)
            
            direccion = direccion.existe_en_db(request)
            
            propiedad.direccion = direccion
            propiedad.arrendador = request.user.profile
            
            try:
                propiedad.save()
            
            except IntegrityError:
                messages.error(request,"Ya existe una propiedad asociada a esa direccion, Propiedad no creada.")
                return redirect('properties')

            # Redirige a properties_list
            messages.success(request, "Propiedad creada exitosamente")
            return redirect('properties')  
        
        else:
            # Combinar errores de form
            all_errors = MultiValueDict()
            for form in [propiedad_form, dir_form, dir_form]:
                for field, errors in form.errors.items():
                    all_errors.appendlist(field, errors)
    
    context = {'propiedad_form': propiedad_form, 'dir_form': dir_form, 'all_errors': all_errors}
    
    return render(request, 'web_app/property.html', context)

@arrendador_required
def edit_property(request, pk):
    propiedad = get_object_or_404(Propiedad, pk=pk)
    propiedad_form = PropiedadForm(request.POST or None, instance=propiedad)
    dir_form = DireccionForm(request.POST or None, instance=propiedad.direccion)
    all_errors = None
        
    if request.method == 'POST':        
        if propiedad_form.is_valid() and dir_form.is_valid():
            # Procesar forms validos
            direccion = dir_form.save(commit = False)
            propiedad = propiedad_form.save(commit = False)
            
            direccion_old = propiedad.direccion
            direccion_new = direccion.existe_en_db(request)
            
            propiedad.direccion = direccion_new
            propiedad.arrendador = request.user.profile
            
            try:
                propiedad.save()
            
            except IntegrityError:
                messages.error(request,"Ya existe una propiedad asociada a esa direccion, Propiedad no actualizada.")
                return redirect('properties')

            asociada_a_profiles = Profile.objects.filter(direccion=direccion_old).first()

            if not asociada_a_profiles and direccion_old.pk != direccion_new.pk:
                direccion_old.delete()
                messages.success(request, "Direccion antigua no estaba asociada. Se elimino.")
            
            # Redirige a properties_list
            messages.success(request, "Propiedad actualizada exitosamente")
            return redirect('properties')  
        
        else:
            # Combinar errores de form
            all_errors = MultiValueDict()
            for form in [propiedad_form, dir_form, dir_form]:
                for field, errors in form.errors.items():
                    all_errors.appendlist(field, errors)
    
    context = {'propiedad_form': propiedad_form, 'dir_form': dir_form, 'all_errors': all_errors , 'editar': True}
    
    return render(request, 'web_app/property.html', context)

@arrendador_required
def delete_property(request, pk):
    propiedad = get_object_or_404(Propiedad, pk=pk)
    
    if request.method == 'POST':
        direccion = propiedad.direccion
        
        propiedad.delete()
        messages.success(request, "Propiedad eliminada exitosamente.")

        asociada_a_profiles = Profile.objects.filter(direccion=direccion).first()

        if not asociada_a_profiles:
            direccion.delete()
            messages.success(request, "Direccion de la propiedad no estaba asociada. Tambien fue eliminada.")
        
        return redirect('properties')

    return render(request, 'web_app/delete_property.html',{'propiedad': propiedad})


def property_detail(request, pk):
    propiedad = get_object_or_404(Propiedad, pk=pk)
    imagenes =propiedad.imagen_set.all()

    return render(request, 'web_app/property_detail.html', {'propiedad': propiedad, 'imagenes': imagenes})


def leases_list(request):
    # Obtener todas las propiedades disponibles
    propiedades = Propiedad.objects.filter(disponible=True).order_by("direccion__comuna__region", "direccion__comuna")
    
    # Get all regions and comunas for the filter dropdowns
    regiones = Region.objects.all()
    comunas = Comuna.objects.all()

    # Obtener los parametros de filtrado
    region_id = request.GET.get('region')
    comuna_id = request.GET.get('comuna')

    # Aplicar Filtros
    if region_id:
        propiedades = propiedades.filter(direccion__comuna__region_id=region_id)
    if comuna_id:
        propiedades = propiedades.filter(direccion__comuna_id=comuna_id)

    context = {
        'propiedades': propiedades,
        'regiones': regiones,
        'comunas': comunas,
        'selected_region': region_id,
        'selected_comuna': comuna_id,
    }

    return render(request, 'web_app/leases_list.html', context)

@arrendador_required
def property_images(request, pk):
    propiedad = get_object_or_404(Propiedad, pk=pk)
    imagenes = Imagen.objects.filter(propiedad__id = pk)
    
    if request.method == "POST":
        if 'add_photo' in request.POST:
            form = ImagenForm(request.POST,request.FILES)
            if form.is_valid():
                imagen = form.save(commit=False)
                imagen.propiedad = propiedad
                imagen.save()
            
        elif 'delete_photo' in request.POST:
            id = request.POST.get('delete_photo')
            imagen = Imagen.objects.get(id=id)

            if os.path.isfile(imagen.foto.path):
                os.remove(imagen.foto.path)
            
            imagen.delete()

        # Redirige al listado de fotos
        return redirect('images', pk=propiedad.id)
    else:
        form = ImagenForm()

    return render(request, 'web_app/property_images.html', {'imagenes': imagenes, 'form': form})