from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.order import Order, OrderItem
from app.models.cart import Cart, CartItem
from app.models.product import Product

bp = Blueprint('orders', __name__, url_prefix='/api/orders')

@bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart or cart.items.count() == 0:
        return {'error': 'Cart is empty'}, 400

    shipping_address = data.get('shipping_address')
    shipping_city = data.get('shipping_city')
    shipping_postal_code = data.get('shipping_postal_code')

    if not all([shipping_address, shipping_city, shipping_postal_code]):
        return {'error': 'Missing shipping information'}, 400

    cart_items = list(cart.items)
    orders_created = []

    for item in cart_items:
        product = item.product
        seller_id = product.seller_id

        total_price = product.price * item.quantity

        order = Order(
            buyer_id=user_id,
            seller_id=seller_id,
            total_price=total_price,
            status='pending',
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_postal_code=shipping_postal_code
        )

        order_item = OrderItem(
            order=order,
            product_id=product.id,
            price_at_purchase=product.price,
            quantity=item.quantity
        )

        product.status = 'sold'

        db.session.add(order)
        db.session.add(order_item)
        orders_created.append(order)

    CartItem.query.filter_by(cart_id=cart.id).delete()
    db.session.commit()

    return {
        'message': 'Orders created',
        'orders': [o.to_dict() for o in orders_created]
    }, 201

@bp.route('', methods=['GET'])
@jwt_required()
def list_orders():
    user_id = int(get_jwt_identity())

    role = request.args.get('role', 'buyer')

    if role == 'seller':
        orders = Order.query.filter_by(seller_id=user_id).all()
    else:
        orders = Order.query.filter_by(buyer_id=user_id).all()

    return {'orders': [o.to_dict() for o in orders]}, 200

@bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.get(order_id)

    if not order or (order.buyer_id != user_id and order.seller_id != user_id):
        return {'error': 'Order not found'}, 404

    return order.to_dict(), 200

@bp.route('/<int:order_id>/status', methods=['PATCH'])
@jwt_required()
def update_order_status(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.get(order_id)

    if not order or order.seller_id != user_id:
        return {'error': 'Order not found'}, 404

    data = request.get_json() or {}
    new_status = data.get('status')

    valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    if new_status not in valid_statuses:
        return {'error': 'Invalid status'}, 400

    order.status = new_status
    db.session.commit()

    return order.to_dict(), 200
