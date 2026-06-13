def test_create_user(db):
    from app.models.user import User
    user = User(username='newuser', email='new@example.com')
    user.set_password('securepass')
    db.session.add(user)
    db.session.commit()

    assert user.id is not None
    assert user.username == 'newuser'
    assert user.check_password('securepass') is True
    assert user.check_password('wrongpass') is False
    assert user.seller_rating == 5.0
    assert user.is_admin is False


def test_user_to_dict(db):
    from app.models.user import User
    user = User(username='dictuser', email='dict@example.com',
                first_name='Test', last_name='User', city='Paris',
                phone='0123456789', address='1 rue Test')
    user.set_password('pass')
    db.session.add(user)
    db.session.commit()

    public = user.to_dict(include_sensitive=False)
    assert public['username'] == 'dictuser'
    assert public['first_name'] == 'Test'
    assert public['email'] is None
    assert public['phone'] is None
    assert public['address'] is None
    assert public['city'] == 'Paris'

    sensitive = user.to_dict(include_sensitive=True)
    assert sensitive['email'] == 'dict@example.com'
    assert sensitive['phone'] == '0123456789'
    assert sensitive['address'] == '1 rue Test'


def test_unique_username(db):
    from app.models.user import User
    import pytest
    from sqlalchemy.exc import IntegrityError

    user1 = User(username='unique', email='a@example.com')
    user1.set_password('pass')
    db.session.add(user1)
    db.session.commit()

    user2 = User(username='unique', email='b@example.com')
    user2.set_password('pass')
    db.session.add(user2)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_create_product(db, seller):
    from app.models.product import Product
    product = Product(
        title='Test Game',
        description='Description',
        category='Jeux de stratégie',
        condition='Neuf',
        price=30.00,
        stock=5,
        seller_id=seller.id,
        number_of_players='2-4',
        playing_time='30 min',
        year=2020
    )
    db.session.add(product)
    db.session.commit()

    assert product.id is not None
    assert product.title == 'Test Game'
    assert product.status == 'available'
    assert product.seller_id == seller.id
    assert product.seller.username == 'seller'


def test_product_to_dict(db, seller):
    from app.models.product import Product
    product = Product(
        title='Dict Game', category='Jeux de party',
        condition='Bon', price=15.00, seller_id=seller.id
    )
    db.session.add(product)
    db.session.commit()

    data = product.to_dict(include_seller=True)
    assert data['title'] == 'Dict Game'
    assert data['seller']['username'] == 'seller'
    assert data['price'] == 15.00

    data_no_seller = product.to_dict(include_seller=False)
    assert data_no_seller['seller_id'] == seller.id
    assert 'seller' not in data_no_seller


def test_cart_creation(db, buyer):
    from app.models.cart import Cart
    cart = Cart(user_id=buyer.id)
    db.session.add(cart)
    db.session.commit()

    assert cart.id is not None
    assert cart.user_id == buyer.id
    assert cart.items.count() == 0
    assert cart.to_dict()['item_count'] == 0
    assert cart.to_dict()['total_price'] == 0


def test_cart_add_item(db, buyer, product):
    from app.models.cart import Cart, CartItem
    cart = Cart(user_id=buyer.id)
    db.session.add(cart)
    db.session.commit()

    item = CartItem(cart_id=cart.id, product_id=product.id, quantity=2)
    db.session.add(item)
    db.session.commit()

    assert cart.items.count() == 1
    cart_dict = cart.to_dict()
    assert cart_dict['item_count'] == 2
    assert cart_dict['total_price'] == product.price * 2


def test_cart_item_subtotal(db, buyer, product):
    from app.models.cart import Cart, CartItem
    cart = Cart(user_id=buyer.id)
    db.session.add(cart)
    db.session.commit()

    item = CartItem(cart_id=cart.id, product_id=product.id, quantity=3)
    db.session.add(item)
    db.session.commit()

    item_dict = item.to_dict()
    assert item_dict['quantity'] == 3
    assert item_dict['subtotal'] == product.price * 3


def test_create_order(db, buyer, seller, product):
    from app.models.order import Order, OrderItem
    order = Order(
        buyer_id=buyer.id,
        seller_id=seller.id,
        total_price=product.price,
        status='pending',
        shipping_address='1 rue Test',
        shipping_city='Paris',
        shipping_postal_code='75001'
    )
    db.session.add(order)
    db.session.flush()

    item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        price_at_purchase=product.price,
        quantity=1
    )
    db.session.add(item)
    db.session.commit()

    assert order.id is not None
    assert order.status == 'pending'
    assert order.buyer_id == buyer.id
    assert order.items.count() == 1

    order_dict = order.to_dict()
    assert order_dict['total_price'] == product.price
    assert len(order_dict['items']) == 1


def test_create_review(db, buyer, seller, product):
    from app.models.order import Order, OrderItem
    from app.models.review import Review

    order = Order(
        buyer_id=buyer.id, seller_id=seller.id,
        total_price=product.price, status='delivered',
        shipping_address='Addr', shipping_city='City',
        shipping_postal_code='12345'
    )
    db.session.add(order)
    db.session.flush()

    OrderItem(order_id=order.id, product_id=product.id,
              price_at_purchase=product.price, quantity=1)
    db.session.flush()

    review = Review(
        reviewer_id=buyer.id,
        seller_id=seller.id,
        product_id=product.id,
        order_id=order.id,
        rating=5,
        title='Super jeu',
        comment='Excellent état, livraison rapide'
    )
    db.session.add(review)
    db.session.commit()

    assert review.id is not None
    assert review.rating == 5
    assert review.reviewer.username == 'buyer'

    review_dict = review.to_dict()
    assert review_dict['rating'] == 5
    assert review_dict['reviewer']['username'] == 'buyer'


def test_wishlist(db, buyer, product):
    from app.models.wishlist import Wishlist
    import pytest
    from sqlalchemy.exc import IntegrityError

    wl = Wishlist(user_id=buyer.id, product_id=product.id)
    db.session.add(wl)
    db.session.commit()

    assert wl.id is not None

    duplicate = Wishlist(user_id=buyer.id, product_id=product.id)
    db.session.add(duplicate)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_message(db, seller, buyer, product):
    from app.models.message import Message

    msg = Message(
        sender_id=buyer.id,
        recipient_id=seller.id,
        product_id=product.id,
        subject='Question sur Catan',
        content='Bonjour, le jeu est-il toujours disponible ?'
    )
    db.session.add(msg)
    db.session.commit()

    assert msg.id is not None
    assert msg.is_read is False
    assert msg.sender.username == 'buyer'
    assert msg.recipient.username == 'seller'

    msg_dict = msg.to_dict()
    assert msg_dict['subject'] == 'Question sur Catan'
    assert msg_dict['sender']['username'] == 'buyer'
