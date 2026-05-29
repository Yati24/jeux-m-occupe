from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.product import Product
from app.models.user import User

bp = Blueprint('selling', __name__, url_prefix='/api/selling')

@bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    required_fields = ['title', 'category', 'condition', 'price']
    if not all(field in data for field in required_fields):
        return {'error': 'Missing required fields'}, 400

    product = Product(
        title=data['title'],
        description=data.get('description', ''),
        category=data['category'],
        condition=data['condition'],
        price=data['price'],
        seller_id=user_id,
        image_url=data.get('image_url'),
        number_of_players=data.get('number_of_players'),
        playing_time=data.get('playing_time'),
        year=data.get('year')
    )

    db.session.add(product)
    db.session.commit()

    return product.to_dict(), 201

@bp.route('/products', methods=['GET'])
@jwt_required()
def list_my_products():
    user_id = get_jwt_identity()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    paginated = Product.query.filter_by(seller_id=user_id).paginate(page=page, per_page=per_page)

    return {
        'products': [p.to_dict() for p in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages
    }, 200

@bp.route('/products/<int:product_id>', methods=['PATCH'])
@jwt_required()
def update_product(product_id):
    user_id = get_jwt_identity()
    product = Product.query.get(product_id)

    if not product or product.seller_id != user_id:
        return {'error': 'Product not found'}, 404

    data = request.get_json() or {}

    updatable_fields = ['title', 'description', 'category', 'condition', 'price', 'image_url', 'number_of_players', 'playing_time', 'year', 'status']

    for field in updatable_fields:
        if field in data:
            setattr(product, field, data[field])

    db.session.commit()
    return product.to_dict(), 200

@bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    user_id = get_jwt_identity()
    product = Product.query.get(product_id)

    if not product or product.seller_id != user_id:
        return {'error': 'Product not found'}, 404

    db.session.delete(product)
    db.session.commit()

    return {'message': 'Product deleted'}, 200
