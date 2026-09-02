

from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from datetime import date, timedelta
from config.database import init_db, db
from config.jwt_keys import load_keys
from controller.user_controller import REVOKED_TOKENS

from models.department import Department
from models.designation import Designation
from models.employee import Employee
from models.user import User
from models.attendance import Attendance
from models.leave_type import LeaveType
from models.leave_request import LeaveRequest
from models.leave_balance import LeaveBalance
from models.employee_document import EmployeeDocument
from models.holiday import Holiday

from controller.employee_controller import employee_controller
from controller.attendance_controller import attendance_controller
from controller.leave_controller import leave_controller
from controller.user_controller import user_controller
from controller.document_controller import document_controller
from controller.holiday_controller import holiday_controller
from flask_jwt_extended import JWTManager


# Load local development secrets from .env before reading configuration.
load_dotenv()

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

app.secret_key = os.getenv("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY is missing. Create a .env file from .env.example.")

# JWT configuration using RSA public/private keys (RS256).
private_key, public_key = load_keys()
app.config["JWT_ALGORITHM"] = "RS256"
app.config["JWT_PRIVATE_KEY"] = private_key
app.config["JWT_PUBLIC_KEY"] = public_key
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
# Browser pages use an HttpOnly JWT cookie.
# CSRF protection is enabled for cookie-based state-changing requests.
app.config["JWT_COOKIE_SECURE"] = os.getenv("JWT_COOKIE_SECURE", "false").lower() == "true"
app.config["JWT_COOKIE_SAMESITE"] = os.getenv("JWT_COOKIE_SAMESITE", "Lax")
app.config["JWT_COOKIE_CSRF_PROTECT"] = True
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie"
app.config["JWT_COOKIE_DOMAIN"] = None
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "15")))
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "30")))

# Harden the browser session used by the server-rendered pages.
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_UPLOAD_MB", "5")) * 1024 * 1024

init_db(app)

jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def is_token_revoked(jwt_header, jwt_payload):
    return jwt_payload["jti"] in REVOKED_TOKENS

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "Unauthorized", "message": "Token has been revoked"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    if request.path.startswith("/api"):
        return jsonify({"error": "Unauthorized", "message": "Bearer access token is required"}), 401
    return jsonify({"error": "Unauthorized"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"error": "Unauthorized", "message": "Invalid or expired token"}), 401

app.register_blueprint(employee_controller)
app.register_blueprint(attendance_controller)
app.register_blueprint(leave_controller)
app.register_blueprint(user_controller)
app.register_blueprint(document_controller)
app.register_blueprint(holiday_controller)


@app.route("/")
def home():
    return render_template("index.html")


def insert_initial_data():

    if Department.query.count() == 0:

        departments = [
            Department(name="Human Resources"),
            Department(name="IT"),
            Department(name="Finance"),
            Department(name="Marketing")
        ]

        db.session.add_all(departments)

    if Designation.query.count() == 0:

        designations = [
            Designation(name="HR Executive"),
            Designation(name="Software Developer"),
            Designation(name="Accountant"),
            Designation(name="Manager")
        ]

        db.session.add_all(designations)

    if LeaveType.query.count() == 0:

        leave_types = [
            LeaveType(name="Casual Leave", days=12),
            LeaveType(name="Sick Leave", days=10),
            LeaveType(name="Earned Leave", days=15)
        ]

        db.session.add_all(leave_types)

    # Starter holiday calendar data. HR can add/remove holidays from the UI.
    if Holiday.query.count() == 0:
        holidays = [
            Holiday(name="Republic Day", holiday_date=date(2026, 1, 26), description="National holiday"),
            Holiday(name="Holi", holiday_date=date(2026, 3, 4), description="Festival holiday"),
            Holiday(name="Good Friday", holiday_date=date(2026, 4, 3), description="Public holiday"),
            Holiday(name="Independence Day", holiday_date=date(2026, 8, 15), description="National holiday"),
            Holiday(name="Gandhi Jayanti", holiday_date=date(2026, 10, 2), description="National holiday"),
            Holiday(name="Diwali", holiday_date=date(2026, 11, 8), description="Festival holiday"),
            Holiday(name="Christmas Day", holiday_date=date(2026, 12, 25), description="Public holiday"),
        ]
        db.session.add_all(holidays)

    db.session.commit()


if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        insert_initial_data()

    app.run(host="0.0.0.0", port=5000, debug=True)