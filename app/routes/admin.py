from flask import Blueprint, request
from sqlalchemy import func
from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.review import Review
from app.models.message import Message
from app.utils.decorators import admin_required

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Commandes considérées comme des ventes réelles (payées et au-delà)
SOLD_STATUSES = ('paid', 'shipped', 'delivered')


@bp.route('/stats', methods=['GET'])
@admin_required
def stats():
    """Statistiques globales pour le dashboard admin."""
    revenue = db.session.query(func.coalesce(func.sum(Order.total_price), 0.0)) \
        .filter(Order.status.in_(SOLD_STATUSES)).scalar()

    avg_rating = db.session.query(func.avg(Review.rating)).scalar()

    week_ago = datetime.utcnow() - timedelta(days=7)

    return {
        'users': User.query.count(),
        'banned_users': User.query.filter_by(is_banned=True).count(),
        'new_users_7d': User.query.filter(User.created_at >= week_ago).count(),
        'products': Product.query.count(),
        'active_listings': Product.query.filter_by(status='available').count(),
        'orders': Order.query.count(),
        'pending_orders': Order.query.filter_by(status='pending').count(),
        'sales': Order.query.filter(Order.status.in_(SOLD_STATUSES)).count(),
        'revenue': round(revenue, 2),
        'reviews': Review.query.count(),
        'avg_rating': round(avg_rating, 2) if avg_rating else None,
        'messages': Message.query.count(),
    }, 200


@bp.route('/sales', methods=['GET'])
@admin_required
def sales():
    """Liste des ventes / commandes (réservé admin)."""
    status = request.args.get('status')
    query = Order.query
    if status:
        query = query.filter_by(status=status)

    orders = query.order_by(Order.created_at.desc()).limit(200).all()

    def user_label(uid):
        u = User.query.get(uid)
        return u.username if u else f'#{uid}'

    return {
        'sales': [
            {
                'id': o.id,
                'buyer': user_label(o.buyer_id),
                'seller': user_label(o.seller_id),
                'total_price': o.total_price,
                'status': o.status,
                'payment_method': o.payment_method,
                'shipping_city': o.shipping_city,
                'tracking_number': o.tracking_number,
                'items_count': o.items.count(),
                'created_at': o.created_at.isoformat() if o.created_at else None,
            }
            for o in orders
        ]
    }, 200


@bp.route('/sales/<int:order_id>/status', methods=['PATCH'])
@admin_required
def update_sale_status(order_id):
    """Modifier le statut d'une commande (ex: annuler un litige)."""
    order = Order.query.get(order_id)
    if not order:
        return {'error': 'Order not found'}, 404

    data = request.get_json() or {}
    new_status = data.get('status')
    valid = ('pending', 'paid', 'shipped', 'delivered', 'cancelled')
    if new_status not in valid:
        return {'error': f'Invalid status, must be one of {valid}'}, 400

    order.status = new_status
    db.session.commit()
    return {'id': order.id, 'status': order.status}, 200


@bp.route('/products', methods=['GET'])
@admin_required
def list_products():
    """Liste des annonces pour la modération."""
    search = request.args.get('search', '').strip()
    query = Product.query
    if search:
        query = query.filter(Product.title.ilike(f'%{search}%'))

    products = query.order_by(Product.created_at.desc()).limit(200).all()
    return {
        'products': [
            {
                'id': p.id,
                'title': p.title,
                'category': p.category,
                'price': p.price,
                'condition': p.condition,
                'stock': p.stock,
                'status': p.status,
                'seller': p.seller.username if p.seller else None,
                'seller_id': p.seller_id,
                'created_at': p.created_at.isoformat() if p.created_at else None,
            }
            for p in products
        ]
    }, 200


@bp.route('/products/<int:product_id>/status', methods=['PATCH'])
@admin_required
def moderate_product(product_id):
    """Masquer / republier une annonce (modération)."""
    product = Product.query.get(product_id)
    if not product:
        return {'error': 'Product not found'}, 404

    data = request.get_json() or {}
    new_status = data.get('status')
    valid = ('available', 'hidden', 'sold')
    if new_status not in valid:
        return {'error': f'Invalid status, must be one of {valid}'}, 400

    product.status = new_status
    db.session.commit()
    return {'id': product.id, 'status': product.status}, 200


@bp.route('/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """Supprimer définitivement une annonce frauduleuse."""
    product = Product.query.get(product_id)
    if not product:
        return {'error': 'Product not found'}, 404

    db.session.delete(product)
    db.session.commit()
    return {'message': 'Product deleted', 'id': product_id}, 200


@bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """Liste tous les utilisateurs (réservé admin)."""
    search = request.args.get('search', '').strip()
    query = User.query
    if search:
        like = f'%{search}%'
        query = query.filter((User.username.ilike(like)) | (User.email.ilike(like)))

    users = query.order_by(User.created_at.desc()).all()
    return {
        'users': [
            {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'city': u.city,
                'seller_rating': u.seller_rating,
                'products_count': u.products.count(),
                'orders_count': u.orders.count(),
                'is_admin': u.is_admin,
                'is_banned': u.is_banned,
                'ban_reason': u.ban_reason,
                'created_at': u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ]
    }, 200


@bp.route('/users/<int:user_id>/ban', methods=['PATCH'])
@admin_required
def ban_user(user_id):
    """Bannir / débannir un utilisateur."""
    from flask_jwt_extended import get_jwt_identity

    user = User.query.get(user_id)
    if not user:
        return {'error': 'User not found'}, 404

    if user.id == int(get_jwt_identity()):
        return {'error': 'Vous ne pouvez pas vous bannir vous-même'}, 400

    if user.is_admin:
        return {'error': 'Impossible de bannir un administrateur'}, 400

    data = request.get_json() or {}
    user.is_banned = bool(data.get('is_banned', True))
    user.ban_reason = data.get('reason') if user.is_banned else None
    db.session.commit()
    return {
        'id': user.id,
        'username': user.username,
        'is_banned': user.is_banned,
        'ban_reason': user.ban_reason,
    }, 200
