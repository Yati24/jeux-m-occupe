from flask_jwt_extended import create_access_token


def _buyer_token(client, db):
    from app.models.user import User
    buyer = User.query.filter_by(username='buyer').first()
    return create_access_token(identity=str(buyer.id))


class TestCreateOrder:
    def test_create_order_success(self, client, buyer_headers, seller, db, product):
        client.post('/api/cart/items', json={
            'product_id': product.id, 'quantity': 2
        }, headers=buyer_headers)

        response = client.post('/api/orders', json={
            'shipping_address': '1 rue Test',
            'shipping_city': 'Paris',
            'shipping_postal_code': '75001'
        }, headers=buyer_headers)
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Orders created'
        assert len(data['orders']) == 1
        assert data['orders'][0]['total_price'] == product.price * 2
        assert data['orders'][0]['status'] == 'pending'

    def test_create_order_multiple_sellers(self, client, buyer_headers, seller, db, product):
        from app.models.user import User
        seller2 = User(username='seller2', email='seller2@example.com')
        seller2.set_password('pass')
        db.session.add(seller2)
        db.session.commit()

        from app.models.product import Product
        other_product = Product(
            title='7 Wonders', category='Jeux de stratégie',
            condition='Très bon', price=30.00, stock=1,
            seller_id=seller2.id, status='available'
        )
        db.session.add(other_product)
        db.session.commit()

        client.post('/api/cart/items', json={'product_id': product.id, 'quantity': 1},
                    headers=buyer_headers)
        client.post('/api/cart/items', json={'product_id': other_product.id, 'quantity': 1},
                    headers=buyer_headers)

        response = client.post('/api/orders', json={
            'shipping_address': '1 rue Test',
            'shipping_city': 'Paris',
            'shipping_postal_code': '75001'
        }, headers=buyer_headers)
        assert response.status_code == 201
        data = response.get_json()
        assert len(data['orders']) == 2

    def test_create_order_empty_cart(self, client, buyer_headers):
        response = client.post('/api/orders', json={
            'shipping_address': '1 rue Test',
            'shipping_city': 'Paris',
            'shipping_postal_code': '75001'
        }, headers=buyer_headers)
        assert response.status_code == 400
        assert 'empty' in response.get_json()['error']

    def test_create_order_missing_shipping(self, client, buyer_headers, db, product):
        client.post('/api/cart/items', json={'product_id': product.id, 'quantity': 1},
                    headers=buyer_headers)

        response = client.post('/api/orders', json={}, headers=buyer_headers)
        assert response.status_code == 400
        assert 'shipping' in response.get_json()['error']

    def test_create_order_marks_product_sold(self, client, buyer_headers, seller, db, product):
        client.post('/api/cart/items', json={'product_id': product.id, 'quantity': 1},
                    headers=buyer_headers)
        client.post('/api/orders', json={
            'shipping_address': 'Addr', 'shipping_city': 'City',
            'shipping_postal_code': '12345'
        }, headers=buyer_headers)

        from app.models.product import Product
        updated = Product.query.get(product.id)
        assert updated.status == 'sold'


class TestListOrders:
    def test_list_orders_as_buyer(self, client, buyer_headers, seller, db, product):
        client.post('/api/cart/items', json={'product_id': product.id, 'quantity': 1},
                    headers=buyer_headers)
        client.post('/api/orders', json={
            'shipping_address': 'Addr', 'shipping_city': 'City',
            'shipping_postal_code': '12345'
        }, headers=buyer_headers)

        response = client.get('/api/orders?role=buyer', headers=buyer_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['orders']) == 1

    def test_list_orders_as_seller(self, client, seller_headers, seller, buyer, db, product):
        token = _buyer_token(client, db)
        buyer_hdrs = {'Authorization': f'Bearer {token}'}

        client.post('/api/cart/items', json={'product_id': product.id, 'quantity': 1},
                    headers=buyer_hdrs)
        client.post('/api/orders', json={
            'shipping_address': 'Addr', 'shipping_city': 'City',
            'shipping_postal_code': '12345'
        }, headers=buyer_hdrs)

        response = client.get('/api/orders?role=seller', headers=seller_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['orders']) == 1


class TestGetOrder:
    def test_get_order_by_buyer(self, client, buyer_headers, seller, db, product):
        client.post('/api/cart/items', json={'product_id': product.id, 'quantity': 1},
                    headers=buyer_headers)
        order_resp = client.post('/api/orders', json={
            'shipping_address': 'Addr', 'shipping_city': 'City',
            'shipping_postal_code': '12345'
        }, headers=buyer_headers)
        order_id = order_resp.get_json()['orders'][0]['id']

        response = client.get(f'/api/orders/{order_id}', headers=buyer_headers)
        assert response.status_code == 200
        assert response.get_json()['id'] == order_id

    def test_get_order_by_seller(self, client, seller_headers, seller, buyer, db, product):
        token = _buyer_token(client, db)
        buyer_hdrs = {'Authorization': f'Bearer {token}'}

        client.post('/api/cart/items', json={'product_id': product.id, 'quantity': 1},
                    headers=buyer_hdrs)
        order_resp = client.post('/api/orders', json={
            'shipping_address': 'Addr', 'shipping_city': 'City',
            'shipping_postal_code': '12345'
        }, headers=buyer_hdrs)
        order_id = order_resp.get_json()['orders'][0]['id']

        response = client.get(f'/api/orders/{order_id}', headers=seller_headers)
        assert response.status_code == 200

    def test_get_order_unauthorized(self, client, buyer_headers, other_headers, seller, db, product):
        client.post('/api/cart/items', json={'product_id': product.id, 'quantity': 1},
                    headers=buyer_headers)
        order_resp = client.post('/api/orders', json={
            'shipping_address': 'Addr', 'shipping_city': 'City',
            'shipping_postal_code': '12345'
        }, headers=buyer_headers)
        order_id = order_resp.get_json()['orders'][0]['id']

        response = client.get(f'/api/orders/{order_id}', headers=other_headers)
        assert response.status_code == 404

    def test_get_order_not_found(self, client, buyer_headers):
        response = client.get('/api/orders/999', headers=buyer_headers)
        assert response.status_code == 404


class TestUpdateOrderStatus:
    def test_update_status_flow(self, client, seller_headers, seller, buyer, db, product):
        token = _buyer_token(client, db)
        buyer_hdrs = {'Authorization': f'Bearer {token}'}

        client.post('/api/cart/items', json={'product_id': product.id, 'quantity': 1},
                    headers=buyer_hdrs)
        order_resp = client.post('/api/orders', json={
            'shipping_address': 'Addr', 'shipping_city': 'City',
            'shipping_postal_code': '12345'
        }, headers=buyer_hdrs)
        order_id = order_resp.get_json()['orders'][0]['id']

        for status in ['confirmed', 'shipped', 'delivered']:
            response = client.patch(f'/api/orders/{order_id}/status', json={'status': status},
                                    headers=seller_headers)
            assert response.status_code == 200
            assert response.get_json()['status'] == status

    def test_update_status_by_buyer_forbidden(self, client, buyer_headers, seller, db, product):
        client.post('/api/cart/items', json={'product_id': product.id, 'quantity': 1},
                    headers=buyer_headers)
        order_resp = client.post('/api/orders', json={
            'shipping_address': 'Addr', 'shipping_city': 'City',
            'shipping_postal_code': '12345'
        }, headers=buyer_headers)
        order_id = order_resp.get_json()['orders'][0]['id']

        response = client.patch(f'/api/orders/{order_id}/status', json={'status': 'shipped'},
                                headers=buyer_headers)
        assert response.status_code == 404

    def test_update_status_invalid(self, client, seller_headers, seller, buyer, db, product):
        token = _buyer_token(client, db)
        buyer_hdrs = {'Authorization': f'Bearer {token}'}

        client.post('/api/cart/items', json={'product_id': product.id, 'quantity': 1},
                    headers=buyer_hdrs)
        order_resp = client.post('/api/orders', json={
            'shipping_address': 'Addr', 'shipping_city': 'City',
            'shipping_postal_code': '12345'
        }, headers=buyer_hdrs)
        order_id = order_resp.get_json()['orders'][0]['id']

        response = client.patch(f'/api/orders/{order_id}/status', json={'status': 'invalid'},
                                headers=seller_headers)
        assert response.status_code == 400
        assert 'Invalid status' in response.get_json()['error']

    def test_update_status_cancel(self, client, seller_headers, seller, buyer, db, product):
        token = _buyer_token(client, db)
        buyer_hdrs = {'Authorization': f'Bearer {token}'}

        client.post('/api/cart/items', json={'product_id': product.id, 'quantity': 1},
                    headers=buyer_hdrs)
        order_resp = client.post('/api/orders', json={
            'shipping_address': 'Addr', 'shipping_city': 'City',
            'shipping_postal_code': '12345'
        }, headers=buyer_hdrs)
        order_id = order_resp.get_json()['orders'][0]['id']

        response = client.patch(f'/api/orders/{order_id}/status', json={'status': 'cancelled'},
                                headers=seller_headers)
        assert response.status_code == 200
        assert response.get_json()['status'] == 'cancelled'

    def test_update_nonexistent_order(self, client, seller_headers):
        response = client.patch('/api/orders/999/status', json={'status': 'confirmed'},
                                headers=seller_headers)
        assert response.status_code == 404
