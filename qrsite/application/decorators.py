from django.contrib.auth.decorators import login_required as django_login_required
from functools import wraps
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)

def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            logger.warning(f"Неавторизованный доступ к {request.path}")
            return redirect(f'auth_required')
        return view_func(request, *args, **kwargs)
    return wrapper