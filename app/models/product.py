from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False, index=True)
    condition = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False, index=True)
    image_url = db.Column(db.String(255))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    status = db.Column(db.String(50), default='available', index=True)
    number_of_players = db.Column(db.String(100))
    playing_time = db.Column(db.String(100))
    min_age = db.Column(db.Integer)
    year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cart_items = db.relationship('CartItem', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')

    def to_dict(self, include_seller=True):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'condition': self.condition,
            'price': self.price,
            'image_url': self.image_url,
            'status': self.status,
            'number_of_players': self.number_of_players,
            'playing_time': self.playing_time,
            'min_age': self.min_age,
            'year': self.year,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_seller:
            data['seller'] = {
                'id': self.seller.id,
                'username': self.seller.username,
                'avatar': self.seller.avatar,
                'rating': self.seller.seller_rating
            }
        else:
            data['seller_id'] = self.seller_id
        return data
