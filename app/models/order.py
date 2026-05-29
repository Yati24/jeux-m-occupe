from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending', index=True)  # pending, paid, shipped, delivered, cancelled
    shipping_address = db.Column(db.String(255))
    shipping_city = db.Column(db.String(100))
    shipping_postal_code = db.Column(db.String(10))
    shipping_carrier = db.Column(db.String(100))  # Mondial Relay, Colissimo, etc.
    tracking_number = db.Column(db.String(100), unique=True, index=True)  # Numéro de suivi
    payment_method = db.Column(db.String(50))  # stripe, paypal, virement, etc.
    payment_intent_id = db.Column(db.String(255), unique=True, index=True)  # Stripe PaymentIntent ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'total_price': self.total_price,
            'status': self.status,
            'shipping_address': self.shipping_address,
            'shipping_city': self.shipping_city,
            'shipping_postal_code': self.shipping_postal_code,
            'shipping_carrier': self.shipping_carrier,
            'tracking_number': self.tracking_number,
            'payment_method': self.payment_method,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    price_at_purchase = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            'id': self.id,
            'product': self.product.to_dict(),
            'price_at_purchase': self.price_at_purchase,
            'quantity': self.quantity
        }
