

from flask import Blueprint, request, jsonify, render_template, session, redirect
from flask_jwt_extended import get_jwt

from service.attendance_service import AttendanceService
from dao.attendance_dao import AttendanceDAO
from utils.auth import role_required as api_role_required

attendance_controller = Blueprint("attendance_controller", __name__)
attendance_service = AttendanceService(AttendanceDAO())


def _api_claims():
    try:
        return get_jwt()
    except Exception:
        return {}


def _allowed_employee(employee_id, claims):
    role = claims.get("role")
    if role in ["hr", "manager"]:
        return True
    return str(claims.get("employee_id")) == str(employee_id)


@attendance_controller.route("/attendance", methods=["GET"])
@api_role_required("hr", "manager", "employee")
def get_attendance():
    employee_id = request.args.get("employee_id")
    claims = _api_claims()

    if claims.get("role") == "employee":
        employee_id = claims.get("employee_id")
    elif not employee_id and claims.get("role") in ["hr", "manager"]:
        employee_id = None

    attendance = (
        attendance_service.get_by_employee(employee_id)
        if employee_id else attendance_service.get_all()
    )
    return jsonify([a.to_dict() for a in attendance]), 200


@attendance_controller.route("/attendance", methods=["POST"])
@api_role_required("hr", "manager", "employee")
def mark_attendance():
    data = request.get_json(silent=True) or {}
    claims = _api_claims()

    if claims.get("role") == "employee":
        data["employee_id"] = claims.get("employee_id")

    try:
        attendance = attendance_service.mark_attendance(data)
        return jsonify({
            "message": "Attendance marked successfully",
            "attendance": attendance.to_dict(),
        }), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@attendance_controller.route("/employee/attendance", methods=["GET", "POST"])
def employee_attendance():
    if "employee_id" not in session:
        return redirect("/login")

    employee_id = session["employee_id"]

    if request.method == "POST":
        try:
            attendance_service.mark_attendance({
                "employee_id": employee_id,
                "status": request.form.get("status"),
                "date": request.form.get("date"),
            })
        except ValueError as exc:
            attendance = attendance_service.get_by_employee(employee_id)
            return render_template("attendance.html", attendance=attendance, error=str(exc))

    attendance = attendance_service.get_by_employee(employee_id)
    return render_template("attendance.html", attendance=attendance)
