
from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    session,
    redirect,
    current_app,
)
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)

from service.user_service import UserService
from dao.user_dao import UserDAO
from models.employee import Employee


user_controller = Blueprint("user_controller", __name__)
user_service = UserService(UserDAO())

ALLOWED_ROLES = {"employee", "manager", "hr"}
REVOKED_TOKENS = set()


def _token_response(user):
    claims = {
        "role": user.role,
        "email": user.email,
        "employee_id": user.employee_id,
    }
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=claims,
    )
    refresh_token = create_refresh_token(identity=str(user.id))
    return access_token, refresh_token


# --------------------------------------------------
# API REGISTER
# --------------------------------------------------

@user_controller.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "employee").strip().lower()
    employee_id = data.get("employee_id")

    if role not in ALLOWED_ROLES:
        return jsonify({"error": "Invalid role"}), 400

    if role in {"employee", "manager"}:
        if employee_id is None:
            return jsonify({
                "error": "employee_id is required for employee and manager accounts"
            }), 400
        try:
            employee_id = int(employee_id)
        except (TypeError, ValueError):
            return jsonify({"error": "employee_id must be an integer"}), 400

        if Employee.query.get(employee_id) is None:
            return jsonify({"error": "Employee profile not found"}), 404
    else:
        employee_id = None

    try:
        user = user_service.register(email, password, role, employee_id)
        access_token, refresh_token = _token_response(user)
        return jsonify({
            "message": "User registered successfully",
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


# --------------------------------------------------
# API LOGIN
# --------------------------------------------------

@user_controller.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}

    try:
        user = user_service.login(
            (data.get("email") or "").strip().lower(),
            data.get("password") or "",
        )
        access_token, refresh_token = _token_response(user)
        return jsonify({
            "message": "Login successful",
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 401


# --------------------------------------------------
# API REFRESH TOKEN
# --------------------------------------------------

@user_controller.route("/api/refresh", methods=["POST"])
@jwt_required(refresh=True)
def api_refresh():
    user_id = get_jwt_identity()
    user = user_service.user_dao.get_by_id(int(user_id))

    if user is None:
        return jsonify({"error": "User not found"}), 404

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role,
            "email": user.email,
            "employee_id": user.employee_id,
        },
    )
    response = jsonify({
        "access_token": access_token,
        "token_type": "Bearer",
    })
    # Also refresh the browser's HttpOnly access-token cookie.
    set_access_cookies(response, access_token)
    return response, 200


# --------------------------------------------------
# API LOGOUT / TOKEN REVOCATION
# --------------------------------------------------

@user_controller.route("/api/logout", methods=["POST"])
@jwt_required()
def api_logout():
    REVOKED_TOKENS.add(get_jwt()["jti"])
    return jsonify({"message": "Token revoked successfully"}), 200


# --------------------------------------------------
# WEB LOGIN
# --------------------------------------------------

@user_controller.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""

    try:
        user = user_service.login(email, password)

        if user.role in ["employee", "manager"]:
            if not user.employee_id:
                return render_template(
                    "login.html",
                    error="No employee profile is linked to this account.",
                )

            employee = Employee.query.get(user.employee_id)
            if employee is None:
                return render_template(
                    "login.html",
                    error="The employee profile linked to this account does not exist.",
                )

        session["user_id"] = user.id
        session["role"] = user.role
        session["employee_id"] = user.employee_id

        # The server-rendered dashboard uses the same JWT authentication
        # as the protected API routes. Store the access token in an
        # HttpOnly cookie so JavaScript cannot read the token directly.
        access_token, refresh_token = _token_response(user)

        if user.role == "hr":
            response = redirect("/hr/dashboard")
        elif user.role == "manager":
            response = redirect("/manager/dashboard")
        else:
            response = redirect("/employee/dashboard")

        set_access_cookies(response, access_token)
        # Keep the refresh token in an HttpOnly cookie so the browser session
        # can obtain a fresh access token without exposing tokens to JavaScript.
        response.set_cookie(
            "refresh_token_cookie",
            refresh_token,
            httponly=True,
            secure=current_app.config.get("JWT_COOKIE_SECURE", False),
            samesite=current_app.config.get("JWT_COOKIE_SAMESITE", "Lax"),
            path="/api/refresh",
        )
        return response

    except ValueError as exc:
        return render_template("login.html", error=str(exc))


# --------------------------------------------------
# WEB REGISTER
# --------------------------------------------------

@user_controller.route("/register", methods=["GET", "POST"])
def register():
    employees = Employee.query.all()

    if request.method == "GET":
        return render_template("register.html", employees=employees)

    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    role = (request.form.get("role") or "").strip().lower()
    employee_id = request.form.get("employee_id")

    if role in ["employee", "manager"]:
        if not employee_id:
            return render_template(
                "register.html",
                employees=employees,
                error="Please select an employee profile.",
            )
        try:
            employee_id = int(employee_id)
        except ValueError:
            return render_template(
                "register.html",
                employees=employees,
                error="Invalid employee selected.",
            )

        if Employee.query.get(employee_id) is None:
            return render_template(
                "register.html",
                employees=employees,
                error="Selected employee does not exist.",
            )
    else:
        employee_id = None

    try:
        user_service.register(email, password, role, employee_id)
        return redirect("/login")
    except ValueError as exc:
        return render_template(
            "register.html",
            employees=employees,
            error=str(exc),
        )


# --------------------------------------------------
# WEB LOGOUT
# --------------------------------------------------

@user_controller.route("/logout")
def logout():
    session.clear()
    response = redirect("/login")
    unset_jwt_cookies(response)
    response.delete_cookie("refresh_token_cookie", path="/api/refresh")
    return response


# --------------------------------------------------
# CURRENT USER API
# --------------------------------------------------

@user_controller.route("/api/me")
@jwt_required()
def current_user():
    user_id = int(get_jwt_identity())
    user = user_service.user_dao.get_by_id(user_id)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user": user.to_dict(),
        "claims": get_jwt(),
    }), 200
