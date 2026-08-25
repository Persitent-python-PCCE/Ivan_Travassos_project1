

from config.database import db


class LeaveType(db.Model):

    __tablename__ = "leave_types"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    days = db.Column(
        db.Integer,
        nullable=False
    )

    leave_requests = db.relationship(
        "LeaveRequest",
        back_populates="leave_type"
    )

    def to_dict(self):

        return {
            "id": self.id,
            "name": self.name,
            "days": self.days
        }