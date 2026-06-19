from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app import db
from app.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    if not data.get('username') or not data.get('email') or not data.get('password'):
        return {'error': 'Missing required fields'}, 400

    if User.query.filter_by(username=data['username']).first():
        return {'error': 'Username already exists'}, 400

    if User.query.filter_by(email=data['email']).first():
        return {'error': 'Email already exists'}, 400

    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', '')
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    return {'message': 'User created', 'access_token': access_token, 'user': user.to_dict()}, 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    if not data.get('email') or not data.get('password'):
        return {'error': 'Missing email or password'}, 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return {'error': 'Invalid credentials'}, 401

    if user.is_banned:
        return {'error': 'Account banned', 'reason': user.ban_reason or 'Compte suspendu'}, 403

    access_token = create_access_token(identity=str(user.id))
    return {'access_token': access_token, 'user': user.to_dict(include_sensitive=True)}, 200

@bp.route('/profile', methods=['GET'])
def get_profile():
    from flask_jwt_extended import jwt_required, get_jwt_identity

    @jwt_required()
    def _get_profile():
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict(include_sensitive=True), 200

    return _get_profile()
