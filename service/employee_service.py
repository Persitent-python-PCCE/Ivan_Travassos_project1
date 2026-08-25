

from models.employee import Employee
from datetime import datetime


class EmployeeService:

    def __init__(self, employee_dao):

        self.employee_dao = employee_dao

    def get_all_employees(self):

        return self.employee_dao.get_all()

    def get_by_name(self, name):

        return self.employee_dao.get_by_name(name)

    def get_employee(self, employee_id):

        employee = self.employee_dao.get_by_id(
            employee_id
        )

        if employee is None:

            raise ValueError(
                "Employee not found"
            )

        return employee

    def create_employee(self, data):

        if not data.get("name"):
            raise ValueError("Name is required")

        if not data.get("email"):
            raise ValueError("Email is required")

        if "@" not in data["email"]:
            raise ValueError("Invalid email")

        if self.employee_dao.get_by_email(
            data["email"]
        ):

            raise ValueError(
                "Email already exists"
            )

        joining_date = None

        if data.get("joining_date"):

            joining_date = datetime.strptime(
                data["joining_date"],
                "%Y-%m-%d"
            ).date()

        employee = Employee(
            name=data["name"],
            email=data["email"],
            phone=data.get("phone"),
            address=data.get("address"),
            department_id=data.get("department_id") or None,
            designation_id=data.get("designation_id") or None,
            manager_id=data.get("manager_id") or None,
            joining_date=joining_date,
            status=data.get(
                "status",
                "active"
            )
        )

        return self.employee_dao.save_employee(
            employee
        )

    def update_employee(
        self,
        employee_id,
        data
    ):

        employee = self.get_employee(
            employee_id
        )

        if data.get("email"):

            existing = self.employee_dao.get_by_email(
                data["email"]
            )

            if existing and existing.id != employee.id:

                raise ValueError(
                    "Email already exists"
                )

            employee.email = data["email"]

        if data.get("name"):
            employee.name = data["name"]

        if "phone" in data:
            employee.phone = data["phone"]

        if "address" in data:
            employee.address = data["address"]

        if "department_id" in data:
            employee.department_id = (
                data["department_id"] or None
            )

        if "designation_id" in data:
            employee.designation_id = (
                data["designation_id"] or None
            )

        if "manager_id" in data:
            employee.manager_id = (
                data["manager_id"] or None
            )

        if "status" in data:
            employee.status = data["status"]

        if data.get("leaving_date"):

            employee.leaving_date = datetime.strptime(
                data["leaving_date"],
                "%Y-%m-%d"
            ).date()

        return self.employee_dao.update(
            employee
        )

    def delete_employee(self, employee_id):

        employee = self.get_employee(
            employee_id
        )

        self.employee_dao.delete(employee)

    def get_team(self, manager_id):

        return self.employee_dao.get_by_manager(
            manager_id
        )