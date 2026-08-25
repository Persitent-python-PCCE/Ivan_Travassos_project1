

import os
from flask import Blueprint, request, jsonify, session, send_file, render_template, redirect
from flask_jwt_extended import get_jwt

from service.document_service import DocumentService
from dao.document_dao import DocumentDAO
from utils.auth import role_required as api_role_required


document_controller = Blueprint("document_controller", __name__)
document_service = DocumentService(DocumentDAO())

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "uploads",
)


def _claims():
    try:
        return get_jwt()
    except Exception:
        return {}


@document_controller.route("/documents", methods=["GET"])
@api_role_required("hr", "manager", "employee")
def get_documents():
    claims = _claims()
    employee_id = request.args.get("employee_id")

    if claims.get("role") == "employee":
        employee_id = claims.get("employee_id")

    if not employee_id:
        return jsonify({"error": "Employee ID required"}), 400

    documents = document_service.get_by_employee(employee_id)
    return jsonify([document.to_dict() for document in documents])


@document_controller.route("/documents", methods=["POST"])
@api_role_required("hr", "manager", "employee")
def upload_document():
    claims = _claims()
    employee_id = request.form.get("employee_id") or claims.get("employee_id")

    if claims.get("role") == "employee":
        employee_id = claims.get("employee_id")

    if not employee_id:
        return jsonify({"error": "Employee ID required"}), 400

    try:
        document = document_service.upload(
            employee_id,
            request.files.get("file"),
            UPLOAD_FOLDER,
        )
        return jsonify({
            "message": "Document uploaded successfully",
            "document": document.to_dict(),
        }), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@document_controller.route("/documents/<int:document_id>/download")
@api_role_required("hr", "manager", "employee")
def download_document(document_id):
    try:
        document = document_service.get_document(document_id)
        claims = _claims()

        if claims.get("role") == "employee" and str(document.employee_id) != str(claims.get("employee_id")):
            return jsonify({"error": "Forbidden"}), 403

        if not os.path.exists(document.file_path):
            return jsonify({"error": "File not found"}), 404

        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=document.filename,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404


@document_controller.route("/employee/documents", methods=["GET", "POST"])
def employee_documents():
    if "employee_id" not in session:
        return redirect("/login")

    employee_id = session["employee_id"]

    if request.method == "POST":
        try:
            document_service.upload(
                employee_id,
                request.files.get("file"),
                UPLOAD_FOLDER,
            )
        except ValueError as exc:
            return render_template(
                "documents.html",
                documents=document_service.get_by_employee(employee_id),
                error=str(exc),
            )

    documents = document_service.get_by_employee(employee_id)
    return render_template("documents.html", documents=documents)
