class TestGetUser:
    def test_get_user_public(self, client, db, seller):
        response = client.get(f'/api/users/{seller.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['username'] == 'seller'
        assert data['first_name'] == 'Jean'
        assert data['products_count'] == 0
        assert 'email' not in data or data['email'] is None

    def test_get_user_not_found(self, client):
        response = client.get('/api/users/999')
        assert response.status_code == 404

    def test_get_user_with_product_count(self, client, db, seller, product):
        response = client.get(f'/api/users/{seller.id}')
        assert response.status_code == 200
        assert response.get_json()['products_count'] == 1


class TestGetCurrentUser:
    def test_get_current_user(self, client, seller_headers, seller):
        response = client.get('/api/users/me', headers=seller_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['username'] == 'seller'
        assert data['email'] == 'seller@example.com'

    def test_get_current_user_unauthenticated(self, client):
        response = client.get('/api/users/me')
        assert response.status_code == 401


class TestUpdateProfile:
    def test_update_profile(self, client, seller_headers, seller):
        response = client.patch('/api/users/me', json={
            'first_name': 'Jean-Michel',
            'bio': 'Passionné de jeux',
            'city': 'Lyon'
        }, headers=seller_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['first_name'] == 'Jean-Michel'
        assert data['bio'] == 'Passionné de jeux'
        assert data['city'] == 'Lyon'

    def test_update_profile_partial(self, client, seller_headers, seller):
        response = client.patch('/api/users/me', json={
            'last_name': 'Dupont'
        }, headers=seller_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['last_name'] == 'Dupont'
        assert data['username'] == 'seller'

    def test_update_profile_unauthenticated(self, client):
        response = client.patch('/api/users/me', json={'first_name': 'Hacker'})
        assert response.status_code == 401


class TestUserProducts:
    def test_get_user_products(self, client, db, seller, product, another_product):
        response = client.get(f'/api/users/{seller.id}/products')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 2
        titles = [p['title'] for p in data['products']]
        assert 'Catan' in titles
        assert 'Ticket to Ride' in titles

    def test_get_user_products_excludes_sold(self, client, db, seller, product, sold_product):
        response = client.get(f'/api/users/{seller.id}/products')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 1
        assert data['products'][0]['title'] == 'Catan'

    def test_get_user_products_not_found(self, client):
        response = client.get('/api/users/999/products')
        assert response.status_code == 404


class TestUserReviews:
    def test_get_user_reviews_empty(self, client, db, seller):
        response = client.get(f'/api/users/{seller.id}/reviews')
        assert response.status_code == 200
        data = response.get_json()
        assert data['reviews'] == []

    def test_get_user_reviews(self, client, db, buyer, seller, product):
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
            reviewer_id=buyer.id, seller_id=seller.id,
            product_id=product.id, order_id=order.id,
            rating=5, comment='Excellent !'
        )
        db.session.add(review)
        db.session.commit()

        response = client.get(f'/api/users/{seller.id}/reviews')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['reviews']) == 1
        assert data['reviews'][0]['rating'] == 5

    def test_get_user_reviews_not_found(self, client):
        response = client.get('/api/users/999/reviews')
        assert response.status_code == 404
