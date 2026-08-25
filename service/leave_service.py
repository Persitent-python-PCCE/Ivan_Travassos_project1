

from models.leave_request import LeaveRequest
from models.leave_balance import LeaveBalance
from models.leave_type import LeaveType
from datetime import datetime


class LeaveService:

    def __init__(self, leave_dao):

        self.leave_dao = leave_dao

    def get_all(self):

        return self.leave_dao.get_all()

    def get_by_employee(self, employee_id):

        return self.leave_dao.get_by_employee(
            employee_id
        )

    def create_leave(self, data):

        if not data.get("employee_id"):
            raise ValueError(
                "Employee ID is required"
            )

        if not data.get("leave_type_id"):
            raise ValueError(
                "Leave type is required"
            )

        if not data.get("start_date"):
            raise ValueError(
                "Start date is required"
            )

        if not data.get("end_date"):
            raise ValueError(
                "End date is required"
            )

        start_date = datetime.strptime(
            data["start_date"],
            "%Y-%m-%d"
        ).date()

        end_date = datetime.strptime(
            data["end_date"],
            "%Y-%m-%d"
        ).date()

        if end_date < start_date:

            raise ValueError(
                "End date cannot be before start date"
            )

        leave_type = LeaveType.query.get(
            data["leave_type_id"]
        )

        if leave_type is None:

            raise ValueError(
                "Leave type not found"
            )

        requested_days = (
            end_date - start_date
        ).days + 1

        balance = LeaveBalance.query.filter_by(
            employee_id=data["employee_id"],
            leave_type_id=data["leave_type_id"]
        ).first()

        if balance is None:

            balance = LeaveBalance(
                employee_id=data["employee_id"],
                leave_type_id=data["leave_type_id"],
                total_days=leave_type.days,
                used_days=0
            )

            from config.database import db

            db.session.add(balance)
            db.session.commit()

        remaining = (
            balance.total_days -
            balance.used_days
        )

        if requested_days > remaining:

            raise ValueError(
                "Insufficient leave balance"
            )

        leave = LeaveRequest(
            employee_id=data["employee_id"],
            leave_type_id=data["leave_type_id"],
            start_date=start_date,
            end_date=end_date,
            reason=data.get("reason"),
            status="pending"
        )

        return self.leave_dao.save(leave)

    def approve_leave(self, leave_id):

        leave = self.leave_dao.get_by_id(
            leave_id
        )

        if leave is None:

            raise ValueError(
                "Leave request not found"
            )

        if leave.status != "pending":

            raise ValueError(
                "Leave request already processed"
            )

        requested_days = (
            leave.end_date -
            leave.start_date
        ).days + 1

        balance = LeaveBalance.query.filter_by(
            employee_id=leave.employee_id,
            leave_type_id=leave.leave_type_id
        ).first()

        if balance is None:

            leave_type = LeaveType.query.get(
                leave.leave_type_id
            )

            balance = LeaveBalance(
                employee_id=leave.employee_id,
                leave_type_id=leave.leave_type_id,
                total_days=leave_type.days,
                used_days=0
            )

            from config.database import db

            db.session.add(balance)
            db.session.commit()

        remaining = (
            balance.total_days -
            balance.used_days
        )

        if requested_days > remaining:

            raise ValueError(
                "Insufficient leave balance"
            )

        balance.used_days += requested_days

        leave.status = "approved"

        return self.leave_dao.update(
            leave
        )

    def reject_leave(self, leave_id):

        leave = self.leave_dao.get_by_id(
            leave_id
        )

        if leave is None:

            raise ValueError(
                "Leave request not found"
            )

        if leave.status != "pending":

            raise ValueError(
                "Leave request already processed"
            )

        leave.status = "rejected"

        return self.leave_dao.update(
            leave
        )

    def get_balances(self, employee_id):

        return LeaveBalance.query.filter_by(
            employee_id=employee_id
        ).all()