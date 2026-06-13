class TestRegister:
    def test_register_success(self, client, db):
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User created'
        assert 'access_token' in data
        assert data['user']['username'] == 'newuser'

    def test_register_missing_fields(self, client):
        response = client.post('/api/auth/register', json={
            'username': 'newuser'
        })
        assert response.status_code == 400
        assert response.get_json()['error'] == 'Missing required fields'

        response = client.post('/api/auth/register', json={})
        assert response.status_code == 400

    def test_register_duplicate_username(self, client, db):
        client.post('/api/auth/register', json={
            'username': 'dupuser', 'email': 'a@example.com', 'password': 'pass'
        })
        response = client.post('/api/auth/register', json={
            'username': 'dupuser', 'email': 'b@example.com', 'password': 'pass'
        })
        assert response.status_code == 400
        assert 'already exists' in response.get_json()['error']

    def test_register_duplicate_email(self, client, db):
        client.post('/api/auth/register', json={
            'username': 'user1', 'email': 'dup@example.com', 'password': 'pass'
        })
        response = client.post('/api/auth/register', json={
            'username': 'user2', 'email': 'dup@example.com', 'password': 'pass'
        })
        assert response.status_code == 400
        assert 'already exists' in response.get_json()['error']


class TestLogin:
    def test_login_success(self, client, db):
        client.post('/api/auth/register', json={
            'username': 'loginuser', 'email': 'login@example.com', 'password': 'mypassword'
        })
        response = client.post('/api/auth/login', json={
            'email': 'login@example.com',
            'password': 'mypassword'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['username'] == 'loginuser'
        assert 'email' in data['user']

    def test_login_wrong_password(self, client, db):
        client.post('/api/auth/register', json={
            'username': 'wpuser', 'email': 'wp@example.com', 'password': 'correct'
        })
        response = client.post('/api/auth/login', json={
            'email': 'wp@example.com',
            'password': 'wrong'
        })
        assert response.status_code == 401
        assert response.get_json()['error'] == 'Invalid credentials'

    def test_login_nonexistent_user(self, client):
        response = client.post('/api/auth/login', json={
            'email': 'nobody@example.com',
            'password': 'whatever'
        })
        assert response.status_code == 401

    def test_login_missing_fields(self, client):
        response = client.post('/api/auth/login', json={'email': 'test@example.com'})
        assert response.status_code == 400


class TestProfile:
    def test_get_profile_authenticated(self, client, db):
        register_resp = client.post('/api/auth/register', json={
            'username': 'profileuser', 'email': 'profile@example.com', 'password': 'pass'
        })
        token = register_resp.get_json()['access_token']

        response = client.get('/api/auth/profile', headers={
            'Authorization': f'Bearer {token}'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['username'] == 'profileuser'
        assert data['email'] == 'profile@example.com'

    def test_get_profile_no_token(self, client):
        response = client.get('/api/auth/profile')
        assert response.status_code == 401

    def test_get_profile_invalid_token(self, client):
        response = client.get('/api/auth/profile', headers={
            'Authorization': 'Bearer invalidtoken'
        })
        assert response.status_code == 422
