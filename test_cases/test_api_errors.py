def test_invalid_employee_api_requires_authentication(client):
    response = client.get("/employees/9999")
    assert response.status_code == 401


def test_invalid_employee_api_with_authentication(client, auth_headers):
    response = client.get("/employees/9999", headers=auth_headers("employee"))
    assert response.status_code == 404


def test_invalid_leave_api_with_authentication(client, auth_headers):
    response = client.put("/leaves/9999/approve", headers=auth_headers("hr"))
    assert response.status_code == 400
    assert "not found" in response.get_json()["error"].lower()
