class TestListProducts:
    def test_list_products_empty(self, client):
        response = client.get('/api/products')
        assert response.status_code == 200
        data = response.get_json()
        assert data['products'] == []
        assert data['total'] == 0

    def test_list_products(self, client, db, product, another_product, sold_product):
        response = client.get('/api/products')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 2
        titles = [p['title'] for p in data['products']]
        assert 'Catan' in titles
        assert 'Ticket to Ride' in titles
        assert 'Splendor' not in titles

    def test_list_products_filter_by_category(self, client, db, product, another_product):
        response = client.get('/api/products?category=Jeux de stratégie')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 1
        assert data['products'][0]['category'] == 'Jeux de stratégie'

    def test_list_products_filter_by_price(self, client, db, product, another_product):
        response = client.get('/api/products?min_price=30')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 1
        assert data['products'][0]['price'] == 35.00

        response = client.get('/api/products?max_price=30')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 1
        assert data['products'][0]['price'] == 25.00

    def test_list_products_pagination(self, client, db, product, another_product):
        response = client.get('/api/products?per_page=1&page=1')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['products']) == 1
        assert data['total'] == 2
        assert data['pages'] == 2

    def test_list_products_sort_by_price_asc(self, client, db, product, another_product):
        response = client.get('/api/products?sort=price&order=asc')
        data = response.get_json()
        prices = [p['price'] for p in data['products']]
        assert prices == sorted(prices)

    def test_list_products_sort_by_price_desc(self, client, db, product, another_product):
        response = client.get('/api/products?sort=price&order=desc')
        data = response.get_json()
        prices = [p['price'] for p in data['products']]
        assert prices == sorted(prices, reverse=True)


class TestGetProduct:
    def test_get_product_success(self, client, db, product):
        response = client.get(f'/api/products/{product.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Catan'
        assert data['seller']['username'] == 'seller'

    def test_get_product_not_found(self, client):
        response = client.get('/api/products/999')
        assert response.status_code == 404


class TestCategories:
    def test_get_categories(self, client, db, product, another_product):
        response = client.get('/api/products/categories')
        assert response.status_code == 200
        data = response.get_json()
        assert 'Jeux de stratégie' in data['categories']
        assert 'Jeux de société' in data['categories']


class TestProductReviews:
    def test_get_reviews_empty(self, client, db, product):
        response = client.get(f'/api/products/{product.id}/reviews')
        assert response.status_code == 200
        data = response.get_json()
        assert data['reviews'] == []

    def test_get_reviews_with_data(self, client, db, product, buyer, seller):
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
            rating=4, title='Bien', comment='Bon jeu'
        )
        db.session.add(review)
        db.session.commit()

        response = client.get(f'/api/products/{product.id}/reviews')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['reviews']) == 1
        assert data['reviews'][0]['rating'] == 4

    def test_get_reviews_product_not_found(self, client):
        response = client.get('/api/products/999/reviews')
        assert response.status_code == 404
