def test_security_badge_removed_from_employee_dashboard(client, login_session):
    login_session("employee")
    response = client.get("/employee/dashboard")
    assert response.status_code == 200
    assert b"JWT + RBAC enabled" not in response.data
    assert b"Protected" not in response.data


def test_holiday_calendar_visible_to_logged_in_user(client, login_session):
    login_session("employee")
    response = client.get("/holidays")
    assert response.status_code == 200
    assert b"Holiday Calendar" in response.data
