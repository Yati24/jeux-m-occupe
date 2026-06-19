from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except:
            return {'error': 'Unauthorized'}, 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Autorise l'accès uniquement aux utilisateurs dont is_admin == True."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models.user import User
        try:
            verify_jwt_in_request()
        except:
            return {'error': 'Unauthorized'}, 401

        user = User.query.get(int(get_jwt_identity()))
        if not user or not user.is_admin:
            return {'error': 'Admin access required'}, 403

        return f(*args, **kwargs)
    return decorated_function
