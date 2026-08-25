

from models.attendance import Attendance
from config.database import db


class AttendanceDAO:

    def get_all(self):

        return Attendance.query.order_by(
            Attendance.date.desc()
        ).all()

    def get_by_employee(self, employee_id):

        return Attendance.query.filter_by(
            employee_id=employee_id
        ).order_by(
            Attendance.date.desc()
        ).all()

    def get_by_employee_date(
        self,
        employee_id,
        attendance_date
    ):

        return Attendance.query.filter_by(
            employee_id=employee_id,
            date=attendance_date
        ).first()

    def save(self, attendance):

        db.session.add(attendance)
        db.session.commit()

        return attendance