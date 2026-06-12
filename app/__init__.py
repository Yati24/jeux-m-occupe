from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
import os

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_name='development'):
    app = Flask(__name__)

    from config import config
    app.config.from_object(config.get(config_name, config['default']))

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    with app.app_context():
        from app.models import user, product, cart, order, review, wishlist, message
        db.create_all()

    from app.routes import auth, products, cart as cart_bp, orders, users, selling
    app.register_blueprint(auth.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(cart_bp.bp)
    app.register_blueprint(orders.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(selling.bp)

    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')

    @app.route('/acheter')
    def acheter():
        from flask import render_template
        return render_template('acheter.html')

    @app.route('/vendre')
    def vendre():
        from flask import render_template
        return render_template('vendre.html')

    @app.route('/panier')
    def panier():
        from flask import render_template
        return render_template('panier.html')

    @app.route('/compte')
    def compte():
        from flask import render_template
        return render_template('compte.html')

    @app.route('/login')
    def login():
        from flask import render_template
        return render_template('login.html')

    @app.route('/register')
    def register():
        from flask import render_template
        return render_template('register.html')

    @app.route('/produit/<int:product_id>')
    def produit(product_id):
        from flask import render_template
        return render_template('produit.html')

    @app.route('/commande')
    def commande():
        from flask import render_template
        return render_template('commande.html')

    @app.route('/commande/<int:order_id>')
    def commande_detail(order_id):
        from flask import render_template
        return render_template('commande.html')

    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request', 'message': str(error)}, 400

    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Unauthorized'}, 401

    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500

    return app
