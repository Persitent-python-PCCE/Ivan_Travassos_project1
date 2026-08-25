def test_create_leave(client, auth_headers):
    response = client.post(
        "/leaves",
        json={
            "employee_id": 1,
            "leave_type_id": 1,
            "start_date": "2026-08-20",
            "end_date": "2026-08-21",
            "reason": "Personal work",
        },
        headers=auth_headers("employee"),
    )
    assert response.status_code == 201
    assert response.get_json()["leave"]["status"] == "pending"
    assert response.get_json()["leave"]["employee_id"] == 1


def test_invalid_leave_dates(client, auth_headers):
    response = client.post(
        "/leaves",
        json={
            "employee_id": 1,
            "leave_type_id": 1,
            "start_date": "2026-08-25",
            "end_date": "2026-08-20",
            "reason": "Test",
        },
        headers=auth_headers("employee"),
    )
    assert response.status_code == 400


def test_leave_without_employee(client, auth_headers):
    response = client.post(
        "/leaves",
        json={
            "leave_type_id": 1,
            "start_date": "2026-08-20",
            "end_date": "2026-08-21",
        },
        headers=auth_headers("hr"),
    )
    assert response.status_code == 400
