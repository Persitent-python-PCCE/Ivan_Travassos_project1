

from models.employee_document import EmployeeDocument
from config.database import db


class DocumentDAO:

    def get_all(self):

        return EmployeeDocument.query.all()

    def get_by_employee(self, employee_id):

        return EmployeeDocument.query.filter_by(
            employee_id=employee_id
        ).all()

    def get_by_id(self, document_id):

        return EmployeeDocument.query.get(document_id)

    def save(self, document):

        db.session.add(document)
        db.session.commit()

        return document

    def delete(self, document):

        db.session.delete(document)
        db.session.commit()