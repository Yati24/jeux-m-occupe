from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    avatar = db.Column(db.String(255))
    bio = db.Column(db.Text)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(10))
    country = db.Column(db.String(100))
    seller_rating = db.Column(db.Float, default=5.0)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    products = db.relationship('Product', backref='seller', lazy='dynamic', foreign_keys='Product.seller_id')
    cart = db.relationship('Cart', backref='user', uselist=False, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='buyer', lazy='dynamic', foreign_keys='Order.buyer_id')
    sold_orders = db.relationship('Order', backref='seller', lazy='dynamic', foreign_keys='Order.seller_id')
    reviews_given = db.relationship('Review', backref='reviewer', lazy='dynamic', foreign_keys='Review.reviewer_id')
    reviews_received = db.relationship('Review', backref='seller_reviewed', lazy='dynamic', foreign_keys='Review.seller_id')
    wishlists = db.relationship('Wishlist', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email if include_sensitive else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'avatar': self.avatar,
            'bio': self.bio,
            'phone': self.phone if include_sensitive else None,
            'address': self.address if include_sensitive else None,
            'city': self.city,
            'seller_rating': self.seller_rating,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }
        return data