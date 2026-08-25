from werkzeug.security import check_password_hash


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_valid_web_login(client):
    response = client.post(
        "/login",
        data={"email": "test@gmail.com", "password": "password123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/employee/dashboard"
    set_cookie = response.headers.get("Set-Cookie", "")
    assert "access_token_cookie=" in set_cookie
    assert "refresh_token_cookie=" in set_cookie


def test_invalid_web_login(client):
    response = client.post(
        "/login",
        data={"email": "wrong@gmail.com", "password": "wrongpassword"},
    )
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_api_login_returns_jwt(client):
    response = client.post(
        "/api/login",
        json={"email": "test@gmail.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["token_type"] == "Bearer"
    assert data["access_token"]
    assert data["refresh_token"]


def test_api_refresh_returns_new_access_token(client):
    login = client.post(
        "/api/login",
        json={"email": "test@gmail.com", "password": "password123"},
    )
    refresh_token = login.get_json()["refresh_token"]

    response = client.post(
        "/api/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert response.status_code == 200
    assert response.get_json()["access_token"]


def test_password_is_hashed(users):
    user = users["employee"]
    assert user.password != "password123"
    assert check_password_hash(user.password, "password123")


def test_unauthorized_hr_dashboard(client):
    response = client.get("/hr/dashboard")
    assert response.status_code == 403
