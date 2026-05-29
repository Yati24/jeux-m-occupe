from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.product import Product
from app.models.user import User

bp = Blueprint('products', __name__, url_prefix='/api/products')

@bp.route('', methods=['GET'])
def list_products():
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    query = Product.query.filter_by(status='available')

    if category:
        query = query.filter_by(category=category)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if order == 'asc':
        query = query.order_by(getattr(Product, sort).asc())
    else:
        query = query.order_by(getattr(Product, sort).desc())

    paginated = query.paginate(page=page, per_page=per_page)

    return {
        'products': [p.to_dict() for p in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }, 200

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return {'error': 'Product not found'}, 404
    return product.to_dict(), 200

@bp.route('/categories', methods=['GET'])
def get_categories():
    categories = db.session.query(Product.category).distinct().all()
    return {'categories': [c[0] for c in categories if c[0]]}, 200

@bp.route('/<int:product_id>/reviews', methods=['GET'])
def get_product_reviews(product_id):
    product = Product.query.get(product_id)
    if not product:
        return {'error': 'Product not found'}, 404

    reviews = product.reviews
    return {'reviews': [r.to_dict() for r in reviews]}, 200
