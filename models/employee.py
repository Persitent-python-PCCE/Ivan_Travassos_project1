

from config.database import db


class Employee(db.Model):

    __tablename__ = "employees"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(20)
    )

    address = db.Column(
        db.String(255)
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id")
    )

    designation_id = db.Column(
        db.Integer,
        db.ForeignKey("designations.id")
    )

    manager_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=True
    )

    joining_date = db.Column(
        db.Date,
        nullable=True
    )

    leaving_date = db.Column(
        db.Date,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        default="active"
    )

    profile_photo = db.Column(
        db.String(255),
        nullable=True
    )

    department = db.relationship(
        "Department",
        back_populates="employees"
    )

    designation = db.relationship(
        "Designation",
        back_populates="employees"
    )

    manager = db.relationship(
        "Employee",
        remote_side=[id],
        backref="team_members"
    )

    def to_dict(self):

        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "department": (
                self.department.name
                if self.department else None
            ),
            "designation": (
                self.designation.name
                if self.designation else None
            ),
            "manager_id": self.manager_id,
            "joining_date": (
                str(self.joining_date)
                if self.joining_date else None
            ),
            "leaving_date": (
                str(self.leaving_date)
                if self.leaving_date else None
            ),
            "status": self.status,
            "profile_photo": self.profile_photo
        }