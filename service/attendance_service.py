

from models.attendance import Attendance
from datetime import date, datetime


class AttendanceService:

    def __init__(self, attendance_dao):

        self.attendance_dao = attendance_dao

    def get_all(self):

        return self.attendance_dao.get_all()

    def get_by_employee(self, employee_id):

        return self.attendance_dao.get_by_employee(
            employee_id
        )

    def mark_attendance(self, data):

        if not data.get("employee_id"):

            raise ValueError(
                "Employee ID is required"
            )

        status = data.get("status")

        if status not in [
            "present",
            "absent",
            "half-day",
            "leave"
        ]:

            raise ValueError(
                "Invalid attendance status"
            )

        attendance_date = date.today()

        if data.get("date"):

            attendance_date = datetime.strptime(
                data["date"],
                "%Y-%m-%d"
            ).date()

        existing = (
            self.attendance_dao
            .get_by_employee_date(
                data["employee_id"],
                attendance_date
            )
        )

        if existing:

            existing.status = status

            from config.database import db

            db.session.commit()

            return existing

        attendance = Attendance(
            employee_id=data["employee_id"],
            date=attendance_date,
            status=status
        )

        return self.attendance_dao.save(
            attendance
        )