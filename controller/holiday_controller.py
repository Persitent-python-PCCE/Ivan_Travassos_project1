from calendar import monthcalendar, month_name
from datetime import date, datetime

from flask import Blueprint, jsonify, redirect, render_template, request, session
from flask_jwt_extended import get_jwt

from config.database import db
from models.holiday import Holiday
from utils.auth import role_required as api_role_required

holiday_controller = Blueprint("holiday_controller", __name__)


def _claims():
    try:
        return get_jwt()
    except Exception:
        return {}


def _logged_in():
    return bool(session.get("user_id"))


@holiday_controller.route("/holidays", methods=["GET"])
def holiday_calendar():
    """Server-rendered holiday calendar for employees, managers and HR."""
    if not _logged_in():
        return redirect("/login")

    today = date.today()
    try:
        year = int(request.args.get("year", today.year))
        month = int(request.args.get("month", today.month))
        selected = date(year, month, 1)
    except (TypeError, ValueError):
        selected = date(today.year, today.month, 1)
        year, month = selected.year, selected.month

    previous = date(year - 1, 12, 1) if month == 1 else date(year, month - 1, 1)
    following = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

    holidays = Holiday.query.filter(
        db.extract("year", Holiday.holiday_date) == year,
        db.extract("month", Holiday.holiday_date) == month,
    ).order_by(Holiday.holiday_date).all()

    holiday_map = {holiday.holiday_date.day: holiday for holiday in holidays}

    upcoming = Holiday.query.filter(
        Holiday.holiday_date >= today
    ).order_by(Holiday.holiday_date).limit(5).all()

    return render_template(
        "holidays.html",
        calendar=monthcalendar(year, month),
        year=year,
        month=month,
        month_name=month_name[month],
        holiday_map=holiday_map,
        holidays=holidays,
        upcoming=upcoming,
        previous=previous,
        following=following,
        today=today,
    )


@holiday_controller.route("/holidays/add", methods=["POST"])
def add_holiday():
    if session.get("role") != "hr":
        return redirect("/holidays")

    name = (request.form.get("name") or "").strip()
    holiday_date = (request.form.get("holiday_date") or "").strip()
    description = (request.form.get("description") or "").strip() or None

    if not name or not holiday_date:
        return redirect("/holidays")

    try:
        parsed_date = datetime.strptime(holiday_date, "%Y-%m-%d").date()
    except ValueError:
        return redirect("/holidays")

    existing = Holiday.query.filter_by(holiday_date=parsed_date).first()
    if existing:
        return redirect(f"/holidays?year={parsed_date.year}&month={parsed_date.month}")

    db.session.add(Holiday(
        name=name,
        holiday_date=parsed_date,
        description=description,
    ))
    db.session.commit()

    return redirect(f"/holidays?year={parsed_date.year}&month={parsed_date.month}")


@holiday_controller.route("/holidays/<int:holiday_id>/delete", methods=["POST"])
def delete_holiday(holiday_id):
    if session.get("role") != "hr":
        return redirect("/holidays")

    holiday = Holiday.query.get(holiday_id)
    if holiday:
        db.session.delete(holiday)
        db.session.commit()

    return redirect("/holidays")


# -----------------------------
# REST API
# -----------------------------

@holiday_controller.route("/api/holidays", methods=["GET"])
@api_role_required("hr", "manager", "employee")
def api_get_holidays():
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    query = Holiday.query
    if year:
        query = query.filter(db.extract("year", Holiday.holiday_date) == year)
    if month:
        query = query.filter(db.extract("month", Holiday.holiday_date) == month)

    holidays = query.order_by(Holiday.holiday_date).all()
    return jsonify([holiday.to_dict() for holiday in holidays]), 200


@holiday_controller.route("/api/holidays", methods=["POST"])
@api_role_required("hr")
def api_add_holiday():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    date_value = (data.get("date") or "").strip()
    description = (data.get("description") or "").strip() or None

    if not name or not date_value:
        return jsonify({"error": "name and date are required"}), 400

    try:
        parsed_date = datetime.strptime(date_value, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "date must use YYYY-MM-DD format"}), 400

    if Holiday.query.filter_by(holiday_date=parsed_date).first():
        return jsonify({"error": "A holiday already exists on this date"}), 409

    holiday = Holiday(
        name=name,
        holiday_date=parsed_date,
        description=description,
    )
    db.session.add(holiday)
    db.session.commit()

    return jsonify({
        "message": "Holiday added successfully",
        "holiday": holiday.to_dict(),
    }), 201


@holiday_controller.route("/api/holidays/<int:holiday_id>", methods=["DELETE"])
@api_role_required("hr")
def api_delete_holiday(holiday_id):
    holiday = Holiday.query.get(holiday_id)
    if not holiday:
        return jsonify({"error": "Holiday not found"}), 404

    db.session.delete(holiday)
    db.session.commit()
    return jsonify({"message": "Holiday deleted successfully"}), 200
