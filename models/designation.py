

from config.database import db


class Designation(db.Model):

    __tablename__ = "designations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    employees = db.relationship(
        "Employee",
        back_populates="designation"
    )

    def to_dict(self):

        return {
            "id": self.id,
            "name": self.name
        }