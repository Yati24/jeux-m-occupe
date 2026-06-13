class TestGetCart:
    def test_get_cart_creates_if_missing(self, client, buyer_headers, buyer, db):
        response = client.get('/api/cart', headers=buyer_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['user_id'] == buyer.id
        assert data['items'] == []
        assert data['item_count'] == 0

    def test_get_cart_unauthenticated(self, client):
        response = client.get('/api/cart')
        assert response.status_code == 401


class TestAddToCart:
    def test_add_to_cart(self, client, buyer_headers, db, product):
        response = client.post('/api/cart/items', json={
            'product_id': product.id,
            'quantity': 2
        }, headers=buyer_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['item_count'] == 2
        assert len(data['items']) == 1

    def test_add_to_cart_default_quantity(self, client, buyer_headers, db, product):
        from app.models.cart import Cart
        response = client.post('/api/cart/items', json={
            'product_id': product.id
        }, headers=buyer_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['item_count'] == 1

    def test_add_existing_product_increments_quantity(self, client, buyer_headers, db, product):
        client.post('/api/cart/items', json={'product_id': product.id, 'quantity': 1},
                    headers=buyer_headers)
        response = client.post('/api/cart/items', json={'product_id': product.id, 'quantity': 2},
                               headers=buyer_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['item_count'] == 3

    def test_add_own_product_forbidden(self, client, seller_headers, db, product):
        response = client.post('/api/cart/items', json={
            'product_id': product.id, 'quantity': 1
        }, headers=seller_headers)
        assert response.status_code == 400
        assert 'votre propre produit' in response.get_json()['error']

    def test_add_unavailable_product(self, client, buyer_headers, db, sold_product):
        response = client.post('/api/cart/items', json={
            'product_id': sold_product.id, 'quantity': 1
        }, headers=buyer_headers)
        assert response.status_code == 400
        assert 'disponible' in response.get_json()['error']

    def test_add_nonexistent_product(self, client, buyer_headers):
        response = client.post('/api/cart/items', json={
            'product_id': 999, 'quantity': 1
        }, headers=buyer_headers)
        assert response.status_code == 404

    def test_add_exceeding_stock(self, client, buyer_headers, db, product):
        response = client.post('/api/cart/items', json={
            'product_id': product.id, 'quantity': 99
        }, headers=buyer_headers)
        assert response.status_code == 400
        assert 'Stock insuffisant' in response.get_json()['error']

    def test_add_invalid_product_id(self, client, buyer_headers):
        response = client.post('/api/cart/items', json={
            'product_id': 'invalid', 'quantity': 1
        }, headers=buyer_headers)
        assert response.status_code == 400

    def test_add_invalid_quantity(self, client, buyer_headers, db, product):
        response = client.post('/api/cart/items', json={
            'product_id': product.id, 'quantity': 0
        }, headers=buyer_headers)
        assert response.status_code == 400

        response = client.post('/api/cart/items', json={
            'product_id': product.id, 'quantity': -1
        }, headers=buyer_headers)
        assert response.status_code == 400

        response = client.post('/api/cart/items', json={
            'product_id': product.id, 'quantity': 'bad'
        }, headers=buyer_headers)
        assert response.status_code == 400


class TestUpdateCartItem:
    def test_update_quantity(self, client, buyer_headers, db, product):
        add_resp = client.post('/api/cart/items', json={
            'product_id': product.id, 'quantity': 1
        }, headers=buyer_headers)
        item_id = add_resp.get_json()['items'][0]['id']

        response = client.patch(f'/api/cart/items/{item_id}', json={
            'quantity': 3
        }, headers=buyer_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['item_count'] == 3

    def test_update_nonexistent_item(self, client, buyer_headers):
        response = client.patch('/api/cart/items/999', json={'quantity': 2},
                                headers=buyer_headers)
        assert response.status_code == 404

    def test_update_other_users_item(self, client, buyer_headers, other_headers, db, product):
        add_resp = client.post('/api/cart/items', json={
            'product_id': product.id, 'quantity': 1
        }, headers=buyer_headers)
        item_id = add_resp.get_json()['items'][0]['id']

        response = client.patch(f'/api/cart/items/{item_id}', json={'quantity': 5},
                                headers=other_headers)
        assert response.status_code == 404

    def test_update_exceeding_stock(self, client, buyer_headers, db, product):
        add_resp = client.post('/api/cart/items', json={
            'product_id': product.id, 'quantity': 1
        }, headers=buyer_headers)
        item_id = add_resp.get_json()['items'][0]['id']

        response = client.patch(f'/api/cart/items/{item_id}', json={'quantity': 99},
                                headers=buyer_headers)
        assert response.status_code == 400


class TestRemoveFromCart:
    def test_remove_item(self, client, buyer_headers, db, product):
        add_resp = client.post('/api/cart/items', json={
            'product_id': product.id, 'quantity': 1
        }, headers=buyer_headers)
        item_id = add_resp.get_json()['items'][0]['id']

        response = client.delete(f'/api/cart/items/{item_id}', headers=buyer_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['item_count'] == 0

    def test_remove_nonexistent_item(self, client, buyer_headers):
        response = client.delete('/api/cart/items/999', headers=buyer_headers)
        assert response.status_code == 404

    def test_remove_other_users_item(self, client, buyer_headers, other_headers, db, product):
        add_resp = client.post('/api/cart/items', json={
            'product_id': product.id, 'quantity': 1
        }, headers=buyer_headers)
        item_id = add_resp.get_json()['items'][0]['id']

        response = client.delete(f'/api/cart/items/{item_id}', headers=other_headers)
        assert response.status_code == 404


class TestClearCart:
    def test_clear_cart(self, client, buyer_headers, db, product):
        client.post('/api/cart/items', json={
            'product_id': product.id, 'quantity': 2
        }, headers=buyer_headers)

        response = client.delete('/api/cart', headers=buyer_headers)
        assert response.status_code == 200
        assert response.get_json()['message'] == 'Cart cleared'

        get_resp = client.get('/api/cart', headers=buyer_headers)
        assert get_resp.get_json()['item_count'] == 0

    def test_clear_empty_cart(self, client, buyer_headers):
        response = client.delete('/api/cart', headers=buyer_headers)
        assert response.status_code == 200
