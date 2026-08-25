from config.database import db


class Holiday(db.Model):
    __tablename__ = "holidays"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    holiday_date = db.Column(db.Date, nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "date": self.holiday_date.isoformat() if self.holiday_date else None,
            "description": self.description,
        }
