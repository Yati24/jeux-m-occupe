import pytest
from app import create_app, db as _db
from app.models.user import User
from app.models.product import Product
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem
from app.models.review import Review
from app.models.wishlist import Wishlist
from app.models.message import Message
from flask_jwt_extended import create_access_token


@pytest.fixture(scope='function')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
    yield app


@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        _db.create_all()
    yield _db
    with app.app_context():
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app, db):
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    return app.test_cli_runner()


def _create_user(db, username='testuser', email='test@example.com', password='password123', **kwargs):
    user = User(username=username, email=email, **kwargs)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def seller(db):
    return _create_user(
        db,
        username='seller',
        email='seller@example.com',
        first_name='Jean',
        last_name='Vendeur',
        seller_rating=4.8
    )


@pytest.fixture
def buyer(db):
    return _create_user(
        db,
        username='buyer',
        email='buyer@example.com',
        first_name='Pierre',
        last_name='Acheteur',
        seller_rating=5.0
    )


@pytest.fixture
def other_user(db):
    return _create_user(
        db,
        username='other',
        email='other@example.com',
        first_name='Autre',
        last_name='Utilisateur'
    )


@pytest.fixture
def product(db, seller):
    product = Product(
        title='Catan',
        description='Jeu en très bon état',
        category='Jeux de stratégie',
        condition='Très bon',
        price=25.00,
        stock=3,
        status='available',
        seller_id=seller.id,
        number_of_players='2-4',
        playing_time='60-90 min',
        year=2015
    )
    db.session.add(product)
    db.session.commit()
    return product


@pytest.fixture
def another_product(db, seller):
    product = Product(
        title='Ticket to Ride',
        description='Édition Europe',
        category='Jeux de société',
        condition='Excellent',
        price=35.00,
        stock=2,
        status='available',
        seller_id=seller.id,
        number_of_players='2-5',
        playing_time='90 min',
        year=2018
    )
    db.session.add(product)
    db.session.commit()
    return product


@pytest.fixture
def sold_product(db, seller):
    product = Product(
        title='Splendor',
        description='Jeu vendu',
        category='Jeux de stratégie',
        condition='Bon',
        price=20.00,
        stock=1,
        status='sold',
        seller_id=seller.id
    )
    db.session.add(product)
    db.session.commit()
    return product


def _auth_header(user):
    token = create_access_token(identity=str(user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def seller_headers(seller):
    return _auth_header(seller)


@pytest.fixture
def buyer_headers(buyer):
    return _auth_header(buyer)


@pytest.fixture
def other_headers(other_user):
    return _auth_header(other_user)
