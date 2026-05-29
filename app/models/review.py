from app import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255))
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    order = db.relationship('Order', backref='reviews')
    product = db.relationship('Product', backref='reviews')

    def to_dict(self):
        return {
            'id': self.id,
            'reviewer': {
                'id': self.reviewer.id,
                'username': self.reviewer.username,
                'avatar': self.reviewer.avatar
            },
            'rating': self.rating,
            'title': self.title,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }
