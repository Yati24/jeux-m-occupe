class TestCreateProduct:
    def test_create_product_success(self, client, seller_headers, db):
        response = client.post('/api/selling/products', json={
            'title': 'Mon Jeu',
            'category': 'Jeux de société',
            'condition': 'Neuf',
            'price': 29.99,
            'description': 'Un super jeu',
            'number_of_players': '2-4',
            'playing_time': '45 min',
            'year': 2020
        }, headers=seller_headers)
        assert response.status_code == 201
        data = response.get_json()
        assert data['title'] == 'Mon Jeu'
        assert data['price'] == 29.99
        assert data['seller']['username'] == 'seller'
        assert data['status'] == 'available'

    def test_create_product_missing_fields(self, client, seller_headers):
        response = client.post('/api/selling/products', json={
            'title': 'Mon Jeu'
        }, headers=seller_headers)
        assert response.status_code == 400

        response = client.post('/api/selling/products', json={}, headers=seller_headers)
        assert response.status_code == 400

    def test_create_product_unauthenticated(self, client):
        response = client.post('/api/selling/products', json={
            'title': 'Test', 'category': 'Test', 'condition': 'Neuf', 'price': 10
        })
        assert response.status_code == 401


class TestListMyProducts:
    def test_list_my_products(self, client, seller_headers, db, product, another_product):
        response = client.get('/api/selling/products', headers=seller_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 2
        titles = [p['title'] for p in data['products']]
        assert 'Catan' in titles
        assert 'Ticket to Ride' in titles

    def test_list_my_products_empty(self, client, buyer_headers):
        response = client.get('/api/selling/products', headers=buyer_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 0
        assert data['products'] == []


class TestUpdateProduct:
    def test_update_product(self, client, seller_headers, db, product):
        response = client.patch(f'/api/selling/products/{product.id}', json={
            'title': 'Catan Updated',
            'price': 30.00
        }, headers=seller_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Catan Updated'
        assert data['price'] == 30.00

    def test_update_other_seller_product(self, client, other_headers, db, product):
        response = client.patch(f'/api/selling/products/{product.id}', json={
            'title': 'Hacked'
        }, headers=other_headers)
        assert response.status_code == 404

    def test_update_nonexistent_product(self, client, seller_headers):
        response = client.patch('/api/selling/products/999', json={'title': 'Nope'},
                                headers=seller_headers)
        assert response.status_code == 404


class TestDeleteProduct:
    def test_delete_product(self, client, seller_headers, db, product):
        response = client.delete(f'/api/selling/products/{product.id}',
                                 headers=seller_headers)
        assert response.status_code == 200
        assert response.get_json()['message'] == 'Product deleted'

        from app.models.product import Product
        assert Product.query.get(product.id) is None

    def test_delete_other_seller_product(self, client, other_headers, db, product):
        response = client.delete(f'/api/selling/products/{product.id}',
                                 headers=other_headers)
        assert response.status_code == 404

    def test_delete_nonexistent_product(self, client, seller_headers):
        response = client.delete('/api/selling/products/999', headers=seller_headers)
        assert response.status_code == 404
