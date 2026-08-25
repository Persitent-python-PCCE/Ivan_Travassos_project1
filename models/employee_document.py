

from config.database import db


class EmployeeDocument(db.Model):

    __tablename__ = "employee_documents"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=False
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    file_path = db.Column(
        db.String(255),
        nullable=False
    )

    employee = db.relationship(
        "Employee"
    )

    def to_dict(self):

        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "filename": self.filename,
            "file_path": self.file_path
        }