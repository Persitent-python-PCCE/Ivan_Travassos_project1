def test_holiday_calendar_page(client, login_session):
    login_session("employee")
    response = client.get("/holidays")
    assert response.status_code == 200
    assert b"Holiday Calendar" in response.data


def test_hr_can_add_holiday(client, login_session):
    login_session("hr")
    response = client.post(
        "/holidays/add",
        data={
            "name": "Founder's Day",
            "holiday_date": "2026-09-15",
            "description": "Company holiday",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/holidays?year=2026&month=9" in response.headers["Location"]


def test_employee_cannot_add_holiday(client, login_session):
    login_session("employee")
    response = client.post(
        "/holidays/add",
        data={
            "name": "Not Allowed",
            "holiday_date": "2026-09-16",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/holidays" in response.headers["Location"]
