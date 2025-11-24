from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
# from django.core.exceptions import PermissionDenied
from functools import wraps
from .models import Profile

def arrendador_required(view_func):
    @wraps(view_func)
    
    # Revisa si usuario esta logeado
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            # Revisa si profile es tipo arrendador y permite acceso a la vista
            if request.user.profile.tipo.nombre == 'arrendador':
                return view_func(request, *args, **kwargs)
            
            # Si profile no es tipo arrendador deniega acceso o redirige
            else:
                # raise PermissionDenied
                return redirect('edit_user')
        
        # Si profile no existe, redirige a login 
        except Profile.DoesNotExist:
            return redirect('login')
    
    return _wrapped_view