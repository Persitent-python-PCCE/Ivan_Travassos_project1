

from config.database import db


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id")
    )

    employee = db.relationship(
        "Employee"
    )

    def to_dict(self):

        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "employee_id": self.employee_id
        }