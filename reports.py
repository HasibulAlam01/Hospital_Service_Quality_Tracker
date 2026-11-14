from database import get_connection
from config import OVERDUE_DAYS


def get_status_counts():
    """Return a dict like {'Pending': 2, 'In Progress': 1, 'Resolved': 0}."""

    counts = {"Pending": 0, "In Progress": 0, "Resolved": 0}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT status, COUNT(*)
        FROM complaints
        GROUP BY status
    """)

    for status, total in cursor.fetchall():
        counts[status] = total

    conn.close()
    return counts


def get_department_counts():
    """Return (department, total, pending, in_progress, resolved)
    for every department."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT d.department_name,
               COUNT(c.complaint_id),
               SUM(CASE WHEN c.status = 'Pending' THEN 1 ELSE 0 END),
               SUM(CASE WHEN c.status = 'In Progress' THEN 1 ELSE 0 END),
               SUM(CASE WHEN c.status = 'Resolved' THEN 1 ELSE 0 END)
        FROM departments d
        LEFT JOIN complaints c
            ON c.department_id = d.department_id
        GROUP BY d.department_id
        ORDER BY COUNT(c.complaint_id) DESC, d.department_name
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_overdue_complaints():
    """Return unresolved complaints older than OVERDUE_DAYS, oldest first.
    Each row: (id, patient, department, subject, status, date, days_open)."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.complaint_id,
               u.full_name,
               d.department_name,
               c.subject,
               c.status,
               c.submitted_at,
               CAST(julianday('now') - julianday(c.submitted_at)
                    AS INTEGER)
        FROM complaints c
        JOIN users u
            ON c.user_id = u.user_id
        JOIN departments d
            ON c.department_id = d.department_id
        WHERE c.status != 'Resolved'
          AND julianday('now') - julianday(c.submitted_at) > ?
        ORDER BY c.submitted_at
    """, (OVERDUE_DAYS,))

    rows = cursor.fetchall()
    conn.close()
    return rows