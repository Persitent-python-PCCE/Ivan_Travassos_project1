

from config.database import db


class Attendance(db.Model):

    __tablename__ = "attendance"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=False
    )

    date = db.Column(
        db.Date,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False
    )

    employee = db.relationship(
        "Employee"
    )

    def to_dict(self):

        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "employee_name": (
                self.employee.name
                if self.employee else None
            ),
            "date": str(self.date),
            "status": self.status
        }