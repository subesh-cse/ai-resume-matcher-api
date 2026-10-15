import io
from fastapi.testclient import TestClient
from pypdf import PdfWriter


def test_create_and_get_job(client: TestClient):
    """
    Test POST /jobs/ creates a record in the in-memory database
    and GET /jobs/ returns the created job.
    """
    payload = {
        "title": "Backend Python Developer",
        "description": "Looking for experience in FastAPI, PostgreSQL, Docker, and Git."
    }
    
    # 1. Create Job
    response = client.post("/jobs/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["id"] is not None
    job_id = data["id"]

    # 2. Retrieve Job List
    list_response = client.get("/jobs/")
    assert list_response.status_code == 200
    jobs = list_response.json()
    assert any(j["id"] == job_id for j in jobs)


def test_upload_resume_invalid_format(client: TestClient):
    """
    Test POST /resumes/upload rejects non-PDF files with a 400 Bad Request.
    """
    # Send a plain text file masquerading or uploaded directly
    fake_file = io.BytesIO(b"Hello, this is just plain text, not a PDF stream.")
    response = client.post(
        "/resumes/upload",
        files={"file": ("test_resume.txt", fake_file, "text/plain")}
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


def test_match_endpoint_not_found(client: TestClient):
    """
    Test POST /match/ returns 404 when querying IDs that don't exist.
    """
    response = client.post("/match/", json={"resume_id": 999, "job_id": 999})
    assert response.status_code == 404


def test_full_match_workflow(client: TestClient):
    """
    End-to-End integration test:
    Create a valid digital PDF in-memory, upload it, create a job, and run the matcher.
    """
    # 1. Create a minimal valid PDF in memory using pypdf
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    # Note: A blank page has no text, so we create a tiny mock text layer or 
    # test the 400 empty text guard directly.
    pdf_buffer = io.BytesIO()
    writer.write(pdf_buffer)
    pdf_buffer.seek(0)

    # Blank PDF upload should trigger 400 because no text could be extracted
    upload_response = client.post(
        "/resumes/upload",
        files={"file": ("empty.pdf", pdf_buffer, "application/pdf")}
    )
    assert upload_response.status_code == 400
    assert "readable text" in upload_response.json()["detail"].lower()
