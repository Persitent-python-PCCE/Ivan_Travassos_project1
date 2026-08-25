

from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    session
)

from service.employee_service import EmployeeService
from dao.employee_dao import EmployeeDAO

from models.department import Department
from models.designation import Designation
from models.employee import Employee
from models.user import User
from models.attendance import Attendance
from models.leave_request import LeaveRequest
from utils.auth import role_required as api_role_required


employee_controller = Blueprint(
    "employee_controller",
    __name__
)

employee_service = EmployeeService(
    EmployeeDAO()
)


def role_required(*roles):

    if "user_id" not in session:

        return False

    return session.get("role") in roles


@employee_controller.route(
    "/employees",
    methods=["GET"]
)
@api_role_required("hr", "manager")
def get_employees():

    if not role_required("hr", "manager"):

        return jsonify({
            "error": "Unauthorized"
        }), 403

    name = request.args.get("name")

    if name:

        employees = employee_service.get_by_name(
            name
        )

    else:

        employees = (
            employee_service
            .get_all_employees()
        )

    return jsonify([
        employee.to_dict()
        for employee in employees
    ])


@employee_controller.route(
    "/employees/add",
    methods=["GET", "POST"]
)
def create_employee():

    if not role_required("hr"):

        return jsonify({
            "error": "HR access required"
        }), 403

    if request.method == "GET":

        departments = Department.query.all()
        designations = Designation.query.all()
        managers = Employee.query.all()

        return render_template(
            "add_employee.html",
            departments=departments,
            designations=designations,
            managers=managers
        )

    data = {
        "name": request.form.get("name"),
        "email": request.form.get("email"),
        "phone": request.form.get("phone"),
        "address": request.form.get("address"),
        "department_id":
            request.form.get("department_id"),
        "designation_id":
            request.form.get("designation_id"),
        "manager_id":
            request.form.get("manager_id"),
        "joining_date":
            request.form.get("joining_date")
    }

    try:

        employee_service.create_employee(
            data
        )

        return redirect("/hr/dashboard")

    except Exception as e:

        departments = Department.query.all()
        designations = Designation.query.all()
        managers = Employee.query.all()

        return render_template(
            "add_employee.html",
            departments=departments,
            designations=designations,
            managers=managers,
            error=str(e)
        )


@employee_controller.route(
    "/employees/<int:employee_id>"
)
@api_role_required("hr", "manager", "employee")
def get_employee(employee_id):

    try:

        employee = employee_service.get_employee(
            employee_id
        )

        return jsonify({
            "message":
                "Employee fetched successfully",
            "employee":
                employee.to_dict()
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 404


@employee_controller.route(
    "/employees/<int:employee_id>",
    methods=["PUT"]
)
@api_role_required("hr")
def update_employee(employee_id):

    if not role_required("hr"):

        return jsonify({
            "error": "HR access required"
        }), 403

    data = request.get_json()

    try:

        employee = employee_service.update_employee(
            employee_id,
            data
        )

        return jsonify({
            "message":
                "Employee updated successfully",
            "employee":
                employee.to_dict()
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400


@employee_controller.route(
    "/employees/<int:employee_id>",
    methods=["DELETE"]
)
@api_role_required("hr")
def delete_employee(employee_id):

    if not role_required("hr"):

        return jsonify({
            "error": "HR access required"
        }), 403

    try:

        employee_service.delete_employee(
            employee_id
        )

        return jsonify({
            "message":
                "Employee deleted successfully"
        })

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400


@employee_controller.route(
    "/employee/dashboard"
)
def employee_dashboard():

    if not role_required(
        "employee",
        "manager",
        "hr"
    ):

        return redirect("/login")

    employee_id = session.get("employee_id")

    if not employee_id:
        return redirect("/login")

    employee = Employee.query.get(employee_id)

    if employee is None:
        session.clear()
        return render_template(
            "login.html",
            error="Employee profile not found for this account"
        ), 404

    attendance = Attendance.query.filter_by(
        employee_id=employee.id
    ).all()

    leaves = LeaveRequest.query.filter_by(
        employee_id=employee.id
    ).all()

    return render_template(
        "employee_dashboard.html",
        employee=employee,
        attendance=attendance,
        leaves=leaves
    )


@employee_controller.route(
    "/employee/profile"
)
def employee_profile():

    if "employee_id" not in session:

        return redirect("/login")

    employee = Employee.query.get(
        session["employee_id"]
    )

    if employee is None:
        session.clear()
        return render_template(
            "login.html",
            error="Employee profile not found for this account"
        ), 404

    return render_template(
        "employee_profile.html",
        employee=employee
    )


@employee_controller.route(
    "/manager/dashboard"
)
def manager_dashboard():

    if not role_required("manager"):

        return jsonify({
            "error": "Manager access required"
        }), 403

    manager = Employee.query.get(
        session.get("employee_id")
    )

    if manager is None:
        session.clear()
        return render_template(
            "login.html",
            error="Manager employee profile not found"
        ), 404

    team = employee_service.get_team(
        manager.id
    )

    pending_leaves = LeaveRequest.query.filter_by(
        status="pending"
    ).filter(
        LeaveRequest.employee_id.in_(
            [employee.id for employee in team]
        )
    ).all()

    return render_template(
        "manager_dashboard.html",
        manager=manager,
        team=team,
        pending_leaves=pending_leaves
    )


@employee_controller.route(
    "/hr/dashboard"
)
def hr_dashboard():

    if not role_required("hr"):

        return jsonify({
            "error": "HR access required"
        }), 403

    employees = Employee.query.all()
    departments = Department.query.all()
    designations = Designation.query.all()

    active = Employee.query.filter_by(
        status="active"
    ).count()

    inactive = Employee.query.filter(
        Employee.status != "active"
    ).count()

    return render_template(
        "hr_dashboard.html",
        employees=employees,
        departments=departments,
        designations=designations,
        active=active,
        inactive=inactive
    )


@employee_controller.route(
    "/departments",
    methods=["GET", "POST"]
)
def departments():

    if not role_required("hr"):

        return jsonify({
            "error": "HR access required"
        }), 403

    if request.method == "GET":

        return jsonify([
            department.to_dict()
            for department in Department.query.all()
        ])

    name = request.json.get("name")

    if not name:

        return jsonify({
            "error": "Department name is required"
        }), 400

    department = Department(name=name)

    from config.database import db

    db.session.add(department)
    db.session.commit()

    return jsonify(
        department.to_dict()
    ), 201


@employee_controller.route(
    "/designations",
    methods=["GET", "POST"]
)
def designations():

    if not role_required("hr"):

        return jsonify({
            "error": "HR access required"
        }), 403

    if request.method == "GET":

        return jsonify([
            designation.to_dict()
            for designation in Designation.query.all()
        ])

    name = request.json.get("name")

    if not name:

        return jsonify({
            "error": "Designation name is required"
        }), 400

    designation = Designation(name=name)

    from config.database import db

    db.session.add(designation)
    db.session.commit()

    return jsonify(
        designation.to_dict()
    ), 201