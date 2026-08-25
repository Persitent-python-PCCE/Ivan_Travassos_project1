import pytest
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

from app import create_app
from config.database import db
from models.department import Department
from models.designation import Designation
from models.employee import Employee
from models.user import User
from models.leave_type import LeaveType


@pytest.fixture
def app():
    test_app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_COOKIE_CSRF_PROTECT": False,
        "JWT_ACCESS_TOKEN_EXPIRES": False,
    })

    with test_app.app_context():
        db.create_all()

        department = Department(name="IT")
        designation = Designation(name="Developer")
        db.session.add_all([department, designation])
        db.session.flush()

        db.session.add_all([
            LeaveType(name="Casual Leave", days=12),
            LeaveType(name="Sick Leave", days=10),
        ])
        db.session.flush()

        employee = Employee(
            name="Test Employee",
            email="test@gmail.com",
            phone="1234567890",
            department_id=department.id,
            designation_id=designation.id,
        )
        manager_employee = Employee(
            name="Test Manager",
            email="manager@gmail.com",
            phone="9876543210",
            department_id=department.id,
            designation_id=designation.id,
        )
        db.session.add_all([employee, manager_employee])
        db.session.flush()

        employee_user = User(
            email="test@gmail.com",
            password=generate_password_hash("password123"),
            role="employee",
            employee_id=employee.id,
        )
        manager_user = User(
            email="manager@gmail.com",
            password=generate_password_hash("Manager@123"),
            role="manager",
            employee_id=manager_employee.id,
        )
        hr_user = User(
            email="hr@gmail.com",
            password=generate_password_hash("Hr@123456"),
            role="hr",
            employee_id=None,
        )
        db.session.add_all([employee_user, manager_user, hr_user])
        db.session.commit()

        yield test_app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def users(app):
    with app.app_context():
        return {
            "employee": User.query.filter_by(email="test@gmail.com").first(),
            "manager": User.query.filter_by(email="manager@gmail.com").first(),
            "hr": User.query.filter_by(email="hr@gmail.com").first(),
        }


def _make_token(app, user):
    with app.app_context():
        return create_access_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role,
                "email": user.email,
                "employee_id": user.employee_id,
            },
        )


@pytest.fixture
def auth_headers(app, users):
    def factory(role="employee"):
        token = _make_token(app, users[role])
        return {"Authorization": f"Bearer {token}"}

    return factory


@pytest.fixture
def login_session(client, users):
    def factory(role="employee"):
        user = users[role]
        with client.session_transaction() as session:
            session["user_id"] = user.id
            session["role"] = user.role
            session["employee_id"] = user.employee_id
        return user

    return factory
