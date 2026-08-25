

from models.employee import Employee
from config.database import db


class EmployeeDAO:

    def get_all(self):

        return Employee.query.all()

    def get_by_id(self, employee_id):

        return Employee.query.get(employee_id)

    def get_by_name(self, name):

        return Employee.query.filter(
            Employee.name.ilike(f"%{name}%")
        ).all()

    def get_by_email(self, email):

        return Employee.query.filter_by(
            email=email
        ).first()

    def get_by_manager(self, manager_id):

        return Employee.query.filter_by(
            manager_id=manager_id
        ).all()

    def save_employee(self, employee):

        db.session.add(employee)
        db.session.commit()

        return employee

    def update(self, employee):

        db.session.commit()

        return employee

    def delete(self, employee):

        db.session.delete(employee)
        db.session.commit()