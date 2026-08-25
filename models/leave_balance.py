

from config.database import db


class LeaveBalance(db.Model):

    __tablename__ = "leave_balances"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=False
    )

    leave_type_id = db.Column(
        db.Integer,
        db.ForeignKey("leave_types.id"),
        nullable=False
    )

    total_days = db.Column(
        db.Integer,
        nullable=False
    )

    used_days = db.Column(
        db.Integer,
        default=0
    )

    employee = db.relationship(
        "Employee"
    )

    leave_type = db.relationship(
        "LeaveType"
    )

    def to_dict(self):

        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "leave_type_id": self.leave_type_id,
            "leave_type": (
                self.leave_type.name
                if self.leave_type else None
            ),
            "total_days": self.total_days,
            "used_days": self.used_days,
            "remaining_days":
                self.total_days - self.used_days
        }