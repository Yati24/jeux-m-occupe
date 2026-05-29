from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User

bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'User not found'}, 404

    products_count = user.products.count()
    reviews_count = user.reviews_received.count()

    data = user.to_dict()
    data['products_count'] = products_count
    data['reviews_count'] = reviews_count

    return data, 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return {'error': 'User not found'}, 404

    return user.to_dict(include_sensitive=True), 200

@bp.route('/me', methods=['PATCH'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return {'error': 'User not found'}, 404

    data = request.get_json() or {}

    updatable_fields = ['first_name', 'last_name', 'bio', 'phone', 'address', 'city', 'postal_code', 'country', 'avatar']

    for field in updatable_fields:
        if field in data:
            setattr(user, field, data[field])

    db.session.commit()
    return user.to_dict(include_sensitive=True), 200

@bp.route('/<int:user_id>/products', methods=['GET'])
def get_user_products(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'User not found'}, 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    paginated = user.products.filter_by(status='available').paginate(page=page, per_page=per_page)

    return {
        'products': [p.to_dict() for p in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages
    }, 200

@bp.route('/<int:user_id>/reviews', methods=['GET'])
def get_user_reviews(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'User not found'}, 404

    reviews = user.reviews_received.all()
    return {'reviews': [r.to_dict() for r in reviews]}, 200
