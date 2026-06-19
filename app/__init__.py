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

    from app.routes import auth, products, cart as cart_bp, orders, users, selling, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(cart_bp.bp)
    app.register_blueprint(orders.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(selling.bp)
    app.register_blueprint(admin.bp)

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

    @app.route('/vendre/<int:product_id>/modifier')
    def modifier_annonce(product_id):
        from flask import render_template, abort
        from app.models.product import Product
        product = Product.query.get(product_id)
        if not product:
            abort(404)
        return render_template('modifier_annonce.html', product=product)

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
        from flask import render_template, abort
        from app.models.product import Product
        product = Product.query.get(product_id)
        if not product:
            abort(404)
        return render_template('produit.html', product=product)

    @app.route('/commande')
    def commande():
        from flask import render_template
        return render_template('commande.html', order_id=None)

    @app.route('/commande/<int:order_id>')
    def commande_detail(order_id):
        from flask import render_template
        return render_template('commande.html', order_id=order_id)

    @app.route('/dashboard')
    def dashboard():
        from flask import render_template
        return render_template('dashboard.html')

    # --- Pages informatives (SEO + maillage interne) ---
    INFO_PAGES = {
        'a-propos': "À propos",
        'mentions-legales': "Mentions légales",
        'cgv': "Conditions générales de vente",
        'confidentialite': "Politique de confidentialité",
    }

    @app.route("/<any('a-propos', 'mentions-legales', 'cgv', 'confidentialite'):slug>")
    def info_page(slug):
        from flask import render_template
        return render_template('info.html', page_title=INFO_PAGES[slug])

    # --- SEO : robots.txt & sitemap.xml ---
    @app.route('/robots.txt')
    def robots_txt():
        from flask import Response, url_for
        sitemap_url = url_for('sitemap_xml', _external=True)
        lines = [
            "User-agent: *",
            "Allow: /",
            "Disallow: /api/",
            "Disallow: /compte",
            "Disallow: /dashboard",
            "Disallow: /panier",
            "Disallow: /commande",
            "Disallow: /login",
            "Disallow: /register",
            f"Sitemap: {sitemap_url}",
        ]
        return Response("\n".join(lines) + "\n", mimetype='text/plain')

    @app.route('/sitemap.xml')
    def sitemap_xml():
        from flask import Response, request
        from xml.sax.saxutils import escape
        from app.models.product import Product

        root = request.url_root.rstrip('/')
        urls = []

        def add(loc, lastmod=None, changefreq='weekly', priority='0.6'):
            entry = [f"<loc>{escape(loc)}</loc>"]
            if lastmod:
                entry.append(f"<lastmod>{lastmod}</lastmod>")
            entry.append(f"<changefreq>{changefreq}</changefreq>")
            entry.append(f"<priority>{priority}</priority>")
            urls.append("<url>" + "".join(entry) + "</url>")

        # Pages statiques
        add(root + '/', changefreq='daily', priority='1.0')
        add(root + '/acheter', changefreq='daily', priority='0.9')
        add(root + '/vendre', priority='0.7')
        for slug in INFO_PAGES:
            add(f"{root}/{slug}", changefreq='yearly', priority='0.3')

        # Fiches produits disponibles
        for p in Product.query.filter_by(status='available').all():
            lastmod = p.updated_at.date().isoformat() if p.updated_at else None
            add(f"{root}/produit/{p.id}", lastmod=lastmod, priority='0.8')

        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
               + "".join(urls) + '</urlset>')
        return Response(xml, mimetype='application/xml')

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
