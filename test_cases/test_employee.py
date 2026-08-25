def test_get_employee_requires_jwt(client):
    response = client.get("/employees/1")
    assert response.status_code == 401


def test_get_existing_employee(client, auth_headers):
    response = client.get("/employees/1", headers=auth_headers("employee"))
    assert response.status_code == 200
    assert response.get_json()["employee"]["email"] == "test@gmail.com"


def test_get_missing_employee(client, auth_headers):
    response = client.get("/employees/9999", headers=auth_headers("employee"))
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_hr_can_create_employee_from_web_form(client, login_session):
    login_session("hr")
    response = client.post(
        "/employees/add",
        data={
            "name": "New Employee",
            "email": "new@gmail.com",
            "phone": "1111111111",
            "department_id": "1",
            "designation_id": "1",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/hr/dashboard"
