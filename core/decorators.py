from functools import wraps

from django.contrib.auth.views import redirect_to_login


def login_required_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return redirect_to_login(request.get_full_path())

    return wrapper
