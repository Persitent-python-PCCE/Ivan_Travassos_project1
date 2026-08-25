
from functools import wraps

from flask import jsonify, request, session
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def api_required(function):
    
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({
                "error": "Unauthorized",
                "message": "A valid Bearer access token is required"
            }), 401
        return function(*args, **kwargs)
    return wrapper


def role_required(*roles):
    """Require a JWT and one of the supplied roles."""
    allowed = {role.lower() for role in roles}

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
            except Exception:
                return jsonify({
                    "error": "Unauthorized",
                    "message": "A valid Bearer access token is required"
                }), 401

            if claims.get("role", "").lower() not in allowed:
                return jsonify({
                    "error": "Forbidden",
                    "message": "You do not have permission to perform this action"
                }), 403

            return function(*args, **kwargs)
        return wrapper
    return decorator


def jwt_claims():
    try:
        return get_jwt()
    except Exception:
        return {}


def current_api_user_id():
    claims = jwt_claims()
    identity = claims.get("sub")
    try:
        return int(identity) if identity is not None else None
    except (TypeError, ValueError):
        return None
