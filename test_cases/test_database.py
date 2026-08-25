from config.database import db
from models.department import Department
from models.designation import Designation
from models.employee import Employee
from models.user import User


def test_database_seeded(client, app):
    with app.app_context():
        assert Department.query.count() == 1
        assert Designation.query.count() == 1
        assert Employee.query.count() == 2
        assert User.query.count() == 3
        assert db.session.query(User).filter_by(email="test@gmail.com").first() is not None
