import os
import shutil
import uuid

from database import get_connection
from config import ATTACHMENT_DIR


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def get_departments():
    """Return all active departments as a list of (id, name)."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT department_id, department_name
        FROM departments
        WHERE is_active = 1
        ORDER BY department_name
    """)

    departments = cursor.fetchall()
    conn.close()

    return departments


def submit_complaint(recorded_by, department_id, patient_name,
                     patient_phone, ward_bed, subject, description):
    """Staff records a complaint for a patient.
    Returns (success, message, complaint_id)."""

    if (not patient_name.strip() or not subject.strip()
            or not description.strip()):
        return (False,
                "Patient name, subject and description are required.",
                None)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO complaints (
                recorded_by,
                department_id,
                patient_name,
                patient_phone,
                ward_bed,
                subject,
                description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            recorded_by,
            department_id,
            patient_name.strip(),
            patient_phone.strip() or None,
            ward_bed.strip() or None,
            subject.strip(),
            description.strip()
        ))

        complaint_id = cursor.lastrowid

        # Record the first status in the history table
        cursor.execute("""
            INSERT INTO status_history (
                complaint_id,
                old_status,
                new_status,
                changed_by
            )
            VALUES (?, NULL, 'Pending', ?)
        """, (complaint_id, recorded_by))

        conn.commit()
        return True, "Complaint recorded successfully!", complaint_id

    except Exception as error:
        conn.rollback()
        return False, f"Could not save complaint: {error}", None

    finally:
        conn.close()


def get_staff_complaints(user_id):
    """Return the complaints recorded by one staff member."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.complaint_id,
               c.patient_name,
               d.department_name,
               c.subject,
               c.status,
               c.submitted_at
        FROM complaints c
        JOIN departments d
            ON c.department_id = d.department_id
        WHERE c.recorded_by = ?
        ORDER BY c.submitted_at DESC, c.complaint_id DESC
    """, (user_id,))

    complaints = cursor.fetchall()
    conn.close()

    return complaints


def get_all_complaints():
    """Return every complaint (for admin use)."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.complaint_id,
               c.patient_name,
               d.department_name,
               c.subject,
               c.status,
               c.submitted_at
        FROM complaints c
        JOIN departments d
            ON c.department_id = d.department_id
        ORDER BY c.submitted_at DESC, c.complaint_id DESC
    """)

    complaints = cursor.fetchall()
    conn.close()

    return complaints


def get_complaint_detail(complaint_id):
    """Return full details of one complaint, or None if not found.
    Row: (id, patient_name, patient_phone, ward_bed, department,
          subject, description, status, submitted_at, recorded_by)"""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.complaint_id,
               c.patient_name,
               c.patient_phone,
               c.ward_bed,
               d.department_name,
               c.subject,
               c.description,
               c.status,
               c.submitted_at,
               u.full_name
        FROM complaints c
        JOIN users u
            ON c.recorded_by = u.user_id
        JOIN departments d
            ON c.department_id = d.department_id
        WHERE c.complaint_id = ?
    """, (complaint_id,))

    row = cursor.fetchone()
    conn.close()

    return row


def save_attachment(complaint_id, source_path):
    """Copy a file into the attachments folder and record it.
    Returns (success, message)."""

    if not os.path.isfile(source_path):
        return False, "File not found."

    file_name = os.path.basename(source_path)
    extension = os.path.splitext(file_name)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        return False, "Only JPG, PNG and PDF files are allowed."

    if os.path.getsize(source_path) > MAX_FILE_SIZE:
        return False, "File is too large. Maximum size is 5 MB."

    # Give the saved file a unique name so nothing is overwritten
    stored_name = uuid.uuid4().hex + extension
    destination = os.path.join(ATTACHMENT_DIR, stored_name)

    shutil.copy2(source_path, destination)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO attachments (
                complaint_id,
                file_name,
                file_path,
                file_type
            )
            VALUES (?, ?, ?, ?)
        """, (
            complaint_id,
            file_name,
            stored_name,
            extension.lstrip(".")
        ))

        conn.commit()
        return True, "Attachment saved successfully!"

    except Exception as error:
        conn.rollback()
        # Remove the copied file if the database save failed
        if os.path.exists(destination):
            os.remove(destination)
        return False, f"Could not save attachment: {error}"

    finally:
        conn.close()


def get_attachments(complaint_id):
    """Return all attachments of one complaint."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT attachment_id,
               file_name,
               file_path,
               file_type,
               uploaded_at
        FROM attachments
        WHERE complaint_id = ?
        ORDER BY uploaded_at
    """, (complaint_id,))

    attachments = cursor.fetchall()
    conn.close()

    return attachments