from database import get_connection


VALID_STATUSES = ["Pending", "In Progress", "Resolved"]


def update_status(complaint_id, new_status, admin_id):
    """Change a complaint's status and record it in the history.
    Returns (success, message)."""

    if new_status not in VALID_STATUSES:
        return False, "Invalid status."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT status FROM complaints WHERE complaint_id = ?",
            (complaint_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return False, "Complaint not found."

        old_status = row[0]

        if old_status == new_status:
            return False, f"Complaint is already '{new_status}'."

        cursor.execute("""
            UPDATE complaints
            SET status = ?
            WHERE complaint_id = ?
        """, (new_status, complaint_id))

        cursor.execute("""
            INSERT INTO status_history (
                complaint_id,
                old_status,
                new_status,
                changed_by
            )
            VALUES (?, ?, ?, ?)
        """, (complaint_id, old_status, new_status, admin_id))

        conn.commit()
        return True, f"Status changed from '{old_status}' to '{new_status}'."

    except Exception as error:
        conn.rollback()
        return False, f"Could not update status: {error}"

    finally:
        conn.close()


def add_remark(complaint_id, admin_id, remark_text):
    """Add an admin remark to a complaint. Returns (success, message)."""

    if not remark_text.strip():
        return False, "Remark cannot be empty."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT complaint_id FROM complaints WHERE complaint_id = ?",
            (complaint_id,)
        )

        if cursor.fetchone() is None:
            return False, "Complaint not found."

        cursor.execute("""
            INSERT INTO remarks (
                complaint_id,
                admin_id,
                remark_text
            )
            VALUES (?, ?, ?)
        """, (complaint_id, admin_id, remark_text.strip()))

        conn.commit()
        return True, "Remark added successfully!"

    except Exception as error:
        conn.rollback()
        return False, f"Could not add remark: {error}"

    finally:
        conn.close()


def get_remarks(complaint_id):
    """Return all remarks of one complaint, oldest first."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.remark_id,
               u.full_name,
               r.remark_text,
               r.created_at
        FROM remarks r
        JOIN users u
            ON r.admin_id = u.user_id
        WHERE r.complaint_id = ?
        ORDER BY r.created_at, r.remark_id
    """, (complaint_id,))

    remarks = cursor.fetchall()
    conn.close()

    return remarks


def get_status_history(complaint_id):
    """Return the full status history of one complaint."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT h.old_status,
               h.new_status,
               u.full_name,
               h.changed_at
        FROM status_history h
        JOIN users u
            ON h.changed_by = u.user_id
        WHERE h.complaint_id = ?
        ORDER BY h.history_id
    """, (complaint_id,))

    history = cursor.fetchall()
    conn.close()

    return history