from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.cart import Cart, CartItem
from app.models.product import Product

bp = Blueprint('cart', __name__, url_prefix='/api/cart')

@bp.route('', methods=['GET'])
@jwt_required()
def get_cart():
    user_id = int(get_jwt_identity())
    cart = Cart.query.filter_by(user_id=user_id).first()

    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()

    return cart.to_dict(), 200

@bp.route('/items', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    product_id = data.get('product_id')
    try:
        product_id = int(product_id)
    except (TypeError, ValueError):
        return {'error': 'product_id must be an integer'}, 400

    quantity = data.get('quantity', 1)
    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return {'error': 'quantity must be a positive integer'}, 400

    product = Product.query.get(product_id)
    if not product:
        return {'error': 'Product not found'}, 404

    if product.status and product.status != 'available':
        return {'error': 'Ce produit n\'est plus disponible'}, 400

    if product.seller_id == user_id:
        return {'error': 'Vous ne pouvez pas ajouter votre propre produit au panier'}, 400

    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()

    existing = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    new_quantity = quantity
    if existing:
        new_quantity += existing.quantity

    if product.stock < new_quantity:
        return {'error': f'Stock insuffisant. Seulement {product.stock} disponible(s).'}, 400

    if existing:
        existing.quantity = new_quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    return cart.to_dict(), 200

@bp.route('/items/<int:item_id>', methods=['PATCH'])
@jwt_required()
def update_cart_item(item_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    quantity = data.get('quantity')
    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return {'error': 'quantity must be a positive integer'}, 400

    item = CartItem.query.get(item_id)
    if not item or item.cart.user_id != user_id:
        return {'error': 'Item not found'}, 404

    if item.product.stock < quantity:
        return {'error': f'Stock insuffisant. Seulement {item.product.stock} disponible(s).'}, 400

    item.quantity = quantity
    db.session.commit()

    return item.cart.to_dict(), 200

@bp.route('/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    user_id = int(get_jwt_identity())
    item = CartItem.query.get(item_id)

    if not item or item.cart.user_id != user_id:
        return {'error': 'Item not found'}, 404

    db.session.delete(item)
    db.session.commit()

    cart = item.cart
    return cart.to_dict(), 200

@bp.route('', methods=['DELETE'])
@jwt_required()
def clear_cart():
    user_id = int(get_jwt_identity())
    cart = Cart.query.filter_by(user_id=user_id).first()

    if cart:
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()

    return {'message': 'Cart cleared'}, 200
