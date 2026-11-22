import sqlite3
from config import DATABASE_PATH


def get_connection():
    """Connect to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    """Create all six database tables."""

    conn = get_connection()
    cursor = conn.cursor()

    # Stop with a clear message if an old-format database is found
    cursor.execute(
        "SELECT sql FROM sqlite_master "
        "WHERE type = 'table' AND name = 'users'"
    )
    row = cursor.fetchone()
    if row and "'patient'" in row[0]:
        conn.close()
        raise RuntimeError(
            "Old database format found. Delete hospital_tracker.db "
            "and start the program again."
        )

    # 1. Users table (hospital staff and admin)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            email TEXT UNIQUE,
            phone TEXT,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('staff', 'admin')),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Departments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            department_id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_name TEXT NOT NULL UNIQUE,
            description TEXT,
            is_active INTEGER DEFAULT 1
        )
    """)

    # 3. Complaints table (recorded by staff for a patient)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            recorded_by INTEGER NOT NULL,
            department_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            patient_phone TEXT,
            ward_bed TEXT,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
                CHECK(status IN ('Pending', 'In Progress', 'Resolved')),
            submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recorded_by) REFERENCES users(user_id),
            FOREIGN KEY (department_id)
                REFERENCES departments(department_id)
        )
    """)

    # 4. Attachments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attachments (
            attachment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (complaint_id)
                REFERENCES complaints(complaint_id)
                ON DELETE CASCADE
        )
    """)

    # 5. Remarks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remarks (
            remark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            admin_id INTEGER NOT NULL,
            remark_text TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (complaint_id)
                REFERENCES complaints(complaint_id)
                ON DELETE CASCADE,
            FOREIGN KEY (admin_id)
                REFERENCES users(user_id)
        )
    """)

    # 6. Status History table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS status_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            old_status TEXT,
            new_status TEXT NOT NULL,
            changed_by INTEGER NOT NULL,
            changed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (complaint_id)
                REFERENCES complaints(complaint_id)
                ON DELETE CASCADE,
            FOREIGN KEY (changed_by)
                REFERENCES users(user_id)
        )
    """)

    # Insert the eight default hospital departments
    departments = [
        ("Emergency", "Emergency medical services"),
        ("Cardiology", "Heart and cardiovascular services"),
        ("Neurology", "Brain and nervous system services"),
        ("Pediatrics", "Child healthcare services"),
        ("Orthopedics", "Bone and joint treatment services"),
        ("Gynecology", "Women's healthcare services"),
        ("Medicine", "General medical services"),
        ("Surgery", "Surgical treatment services")
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO departments
        (department_name, description)
        VALUES (?, ?)
    """, departments)

    conn.commit()
    conn.close()

    print("Database created successfully!")
    print("All six tables are ready.")
    print("Eight hospital departments added.")


if __name__ == "__main__":
    create_tables()