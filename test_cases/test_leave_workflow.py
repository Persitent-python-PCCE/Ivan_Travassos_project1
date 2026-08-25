def _create_leave(client, auth_headers, start="2026-08-20", end="2026-08-21"):
    response = client.post(
        "/leaves",
        json={
            "employee_id": 1,
            "leave_type_id": 1,
            "start_date": start,
            "end_date": end,
            "reason": "Personal",
        },
        headers=auth_headers("employee"),
    )
    assert response.status_code == 201
    return response.get_json()["leave"]["id"]


def test_approve_leave(client, auth_headers):
    leave_id = _create_leave(client, auth_headers)
    response = client.put(
        f"/leaves/{leave_id}/approve",
        headers=auth_headers("hr"),
    )
    assert response.status_code == 200
    assert response.get_json()["leave"]["status"] == "approved"


def test_reject_leave(client, auth_headers):
    leave_id = _create_leave(client, auth_headers, "2026-08-22", "2026-08-23")
    response = client.put(
        f"/leaves/{leave_id}/reject",
        headers=auth_headers("manager"),
    )
    assert response.status_code == 200
    assert response.get_json()["leave"]["status"] == "rejected"


def test_employee_cannot_approve_leave(client, auth_headers):
    leave_id = _create_leave(client, auth_headers)
    response = client.put(
        f"/leaves/{leave_id}/approve",
        headers=auth_headers("employee"),
    )
    assert response.status_code == 403
