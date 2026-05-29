from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending', index=True)
    shipping_address = db.Column(db.String(255))
    shipping_city = db.Column(db.String(100))
    shipping_postal_code = db.Column(db.String(10))
    payment_method = db.Column(db.String(50))
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
