# app/utils/auth_required.py

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt

def role_required(roles):
    """
    Decorador genérico para restringir acesso a usuários com papéis específicos.
    :param roles: Lista de papéis permitidos (ex.: ["admin", "organizer"])
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            jwt_data = get_jwt()
            user_role = jwt_data.get("role", None)

            if user_role not in roles:
                return jsonify({
                    "error": "Permissão negada",
                    "message": f"Acesso permitido apenas para: {', '.join(roles)}"
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


# Decores específicos
def admin_required(fn):
    return role_required(["admin"])(fn)

def organizer_required(fn):
    return role_required(["organizer"])(fn)

def organizer_admin_required(fn):
    return role_required(["organizer-admin"])(fn)

def admin_or_organizer_required(fn):
    return role_required(["admin", "organizer", "organizer-admin"])(fn)
