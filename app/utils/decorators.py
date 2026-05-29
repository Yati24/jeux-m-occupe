from flask_jwt_extended import verify_jwt_in_request
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
