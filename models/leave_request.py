

from config.database import db


class LeaveRequest(db.Model):

    __tablename__ = "leave_requests"

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

    start_date = db.Column(
        db.Date,
        nullable=False
    )

    end_date = db.Column(
        db.Date,
        nullable=False
    )

    reason = db.Column(
        db.String(255)
    )

    status = db.Column(
        db.String(20),
        default="pending"
    )

    employee = db.relationship(
        "Employee"
    )

    leave_type = db.relationship(
        "LeaveType",
        back_populates="leave_requests"
    )

    def to_dict(self):

        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "employee_name": (
                self.employee.name
                if self.employee else None
            ),
            "leave_type_id": self.leave_type_id,
            "leave_type": (
                self.leave_type.name
                if self.leave_type else None
            ),
            "start_date": str(self.start_date),
            "end_date": str(self.end_date),
            "reason": self.reason,
            "status": self.status
        }