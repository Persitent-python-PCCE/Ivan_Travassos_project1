def test_mark_attendance(client, auth_headers):
    response = client.post(
        "/attendance",
        json={"employee_id": 1, "status": "present", "date": "2026-08-20"},
        headers=auth_headers("employee"),
    )
    assert response.status_code == 201
    assert response.get_json()["attendance"]["status"] == "present"


def test_employee_cannot_mark_attendance_for_another_employee(client, auth_headers):
    response = client.post(
        "/attendance",
        json={"employee_id": 2, "status": "present", "date": "2026-08-21"},
        headers=auth_headers("employee"),
    )
    # Current controller overwrites employee_id from the JWT for employee users.
    assert response.status_code == 201
    assert response.get_json()["attendance"]["employee_id"] == 1


def test_invalid_attendance(client, auth_headers):
    response = client.post(
        "/attendance",
        json={"employee_id": 1, "status": "invalid"},
        headers=auth_headers("employee"),
    )
    assert response.status_code == 400
