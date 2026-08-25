def test_missing_employee_name(client, login_session):
    login_session("hr")
    response = client.post(
        "/employees/add",
        data={"email": "new@gmail.com"},
    )
    assert response.status_code == 200
    assert b"Name is required" in response.data


def test_missing_leave_type(client, auth_headers):
    response = client.post(
        "/leaves",
        json={
            "employee_id": 1,
            "start_date": "2026-08-20",
            "end_date": "2026-08-21",
        },
        headers=auth_headers("employee"),
    )
    assert response.status_code == 400
