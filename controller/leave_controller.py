

from flask import Blueprint, request, jsonify, render_template, session, redirect
from flask_jwt_extended import get_jwt

from service.leave_service import LeaveService
from dao.leave_dao import LeaveDAO
from models.leave_type import LeaveType
from utils.auth import role_required as api_role_required

leave_controller = Blueprint("leave_controller", __name__)
leave_service = LeaveService(LeaveDAO())


def _claims():
    try:
        return get_jwt()
    except Exception:
        return {}


@leave_controller.route("/leaves", methods=["GET"])
@api_role_required("hr", "manager", "employee")
def get_leaves():
    claims = _claims()
    employee_id = request.args.get("employee_id")

    if claims.get("role") == "employee":
        employee_id = claims.get("employee_id")

    leaves = (
        leave_service.get_by_employee(employee_id)
        if employee_id else leave_service.get_all()
    )
    return jsonify([leave.to_dict() for leave in leaves]), 200


@leave_controller.route("/leaves", methods=["POST"])
@api_role_required("hr", "manager", "employee")
def create_leave():
    data = request.get_json(silent=True) or {}
    claims = _claims()

    if claims.get("role") == "employee":
        data["employee_id"] = claims.get("employee_id")

    try:
        leave = leave_service.create_leave(data)
        return jsonify({
            "message": "Leave request created",
            "leave": leave.to_dict(),
        }), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@leave_controller.route("/leaves/<int:leave_id>/approve", methods=["PUT"])
@api_role_required("manager", "hr")
def approve_leave(leave_id):
    try:
        leave = leave_service.approve_leave(leave_id)
        return jsonify({"message": "Leave approved", "leave": leave.to_dict()}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@leave_controller.route("/leaves/<int:leave_id>/reject", methods=["PUT"])
@api_role_required("manager", "hr")
def reject_leave(leave_id):
    try:
        leave = leave_service.reject_leave(leave_id)
        return jsonify({"message": "Leave rejected", "leave": leave.to_dict()}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@leave_controller.route("/employee/leave", methods=["GET", "POST"])
def employee_leave():
    if "employee_id" not in session:
        return redirect("/login")

    employee_id = session["employee_id"]

    if request.method == "POST":
        try:
            leave_service.create_leave({
                "employee_id": employee_id,
                "leave_type_id": request.form.get("leave_type_id"),
                "start_date": request.form.get("start_date"),
                "end_date": request.form.get("end_date"),
                "reason": request.form.get("reason"),
            })
        except ValueError as exc:
            return render_template(
                "leave.html",
                leave_types=LeaveType.query.all(),
                leaves=leave_service.get_by_employee(employee_id),
                balances=leave_service.get_balances(employee_id),
                error=str(exc),
            )

    return render_template(
        "leave.html",
        leave_types=LeaveType.query.all(),
        leaves=leave_service.get_by_employee(employee_id),
        balances=leave_service.get_balances(employee_id),
    )


@leave_controller.route("/leave/balances/<int:employee_id>")
@api_role_required("hr", "manager", "employee")
def leave_balances(employee_id):
    claims = _claims()
    if claims.get("role") == "employee" and str(claims.get("employee_id")) != str(employee_id):
        return jsonify({"error": "Forbidden", "message": "You can only view your own balance"}), 403

    return jsonify([
        balance.to_dict()
        for balance in leave_service.get_balances(employee_id)
    ])
