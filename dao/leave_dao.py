

from models.leave_request import LeaveRequest
from config.database import db


class LeaveDAO:

    def get_all(self):

        return LeaveRequest.query.order_by(
            LeaveRequest.start_date.desc()
        ).all()

    def get_by_employee(self, employee_id):

        return LeaveRequest.query.filter_by(
            employee_id=employee_id
        ).order_by(
            LeaveRequest.start_date.desc()
        ).all()

    def get_by_id(self, leave_id):

        return LeaveRequest.query.get(leave_id)

    def save(self, leave):

        db.session.add(leave)
        db.session.commit()

        return leave

    def update(self, leave):

        db.session.commit()

        return leave