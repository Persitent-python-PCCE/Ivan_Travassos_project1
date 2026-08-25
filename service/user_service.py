

import re
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash


class UserService:

    def __init__(self, user_dao):
        self.user_dao = user_dao

    def login(self, email, password):
        if not email or not password:
            raise ValueError("Email and password are required")

        user = self.user_dao.get_by_email(email.lower())
        if user is None or not check_password_hash(user.password, password):
            raise ValueError("Invalid email or password")

        return user

    def register(self, email, password, role, employee_id):
        email = (email or "").strip().lower()
        role = (role or "").strip().lower()

        if not email or not password:
            raise ValueError("Email and password are required")

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("Invalid email address")

        if len(password) < 8:
            raise ValueError("Password must contain at least 8 characters")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValueError("Password must contain at least one special character")

        if role not in {"employee", "manager", "hr"}:
            raise ValueError("Invalid role")

        if self.user_dao.get_by_email(email):
            raise ValueError("Email already registered")

        user = User(
            email=email,
            password=generate_password_hash(password),
            role=role,
            employee_id=employee_id,
        )
        return self.user_dao.save(user)
