import io


def test_document_upload(client, auth_headers, tmp_path, monkeypatch):
    import controller.document_controller as controller
    monkeypatch.setattr(controller, "UPLOAD_FOLDER", str(tmp_path))

    response = client.post(
        "/documents",
        data={"employee_id": "1", "file": (io.BytesIO(b"test document"), "certificate.pdf")},
        content_type="multipart/form-data",
        headers=auth_headers("employee"),
    )
    assert response.status_code == 201
    assert response.get_json()["document"]["filename"] == "certificate.pdf"


def test_invalid_document_type(client, auth_headers, tmp_path, monkeypatch):
    import controller.document_controller as controller
    monkeypatch.setattr(controller, "UPLOAD_FOLDER", str(tmp_path))

    response = client.post(
        "/documents",
        data={"employee_id": "1", "file": (io.BytesIO(b"test"), "virus.exe")},
        content_type="multipart/form-data",
        headers=auth_headers("employee"),
    )
    assert response.status_code == 400
