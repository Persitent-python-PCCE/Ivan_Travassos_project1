

import os

from models.employee_document import EmployeeDocument
from werkzeug.utils import secure_filename


class DocumentService:

    ALLOWED_EXTENSIONS = {
        "pdf",
        "png",
        "jpg",
        "jpeg",
        "doc",
        "docx"
    }

    def __init__(self, document_dao):

        self.document_dao = document_dao

    def get_by_employee(self, employee_id):

        return self.document_dao.get_by_employee(
            employee_id
        )

    def get_document(self, document_id):

        document = self.document_dao.get_by_id(
            document_id
        )

        if document is None:

            raise ValueError(
                "Document not found"
            )

        return document

    def upload(
        self,
        employee_id,
        file,
        upload_folder
    ):

        if file is None:

            raise ValueError(
                "File is required"
            )

        if not file.filename:

            raise ValueError(
                "File name is required"
            )

        filename = secure_filename(
            file.filename
        )

        extension = (
            filename.rsplit(".", 1)[1].lower()
            if "." in filename
            else ""
        )

        if extension not in self.ALLOWED_EXTENSIONS:

            raise ValueError(
                "File type not allowed"
            )

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        file_path = os.path.join(
            upload_folder,
            filename
        )

        counter = 1

        original_path = file_path

        while os.path.exists(file_path):

            name, ext = os.path.splitext(
                original_path
            )

            file_path = (
                f"{name}_{counter}{ext}"
            )

            counter += 1

        file.save(file_path)

        document = EmployeeDocument(
            employee_id=employee_id,
            filename=os.path.basename(file_path),
            file_path=file_path
        )

        return self.document_dao.save(
            document
        )

    def delete(self, document_id):

        document = self.get_document(
            document_id
        )

        if os.path.exists(document.file_path):

            os.remove(document.file_path)

        self.document_dao.delete(document)