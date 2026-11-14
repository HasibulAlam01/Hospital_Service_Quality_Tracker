import os
import sqlite3
from datetime import datetime

from config import BACKUP_DIR
from database import get_connection


REQUIRED_TABLES = {
    "users", "departments", "complaints",
    "attachments", "remarks", "status_history",
}


def create_backup(prefix="backup"):
    """Save a copy of the database. Returns (success, message, path)."""

    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    name = f"{prefix}_{stamp}.db"
    path = os.path.join(BACKUP_DIR, name)

    source = None
    target = None

    try:
        source = get_connection()
        target = sqlite3.connect(path)
        source.backup(target)
        return True, f"Backup created: {name}", path

    except Exception as error:
        return False, f"Backup failed: {error}", None

    finally:
        if target is not None:
            target.close()
        if source is not None:
            source.close()


def list_backups():
    """Return backups as (name, path, size_kb, modified), newest first."""

    backups = []

    for name in os.listdir(BACKUP_DIR):
        if not name.lower().endswith(".db"):
            continue

        path = os.path.join(BACKUP_DIR, name)
        modified = datetime.fromtimestamp(os.path.getmtime(path))

        backups.append((
            name,
            path,
            max(1, os.path.getsize(path) // 1024),
            modified.strftime("%Y-%m-%d %H:%M"),
            os.path.getmtime(path),
        ))

    backups.sort(key=lambda item: item[4], reverse=True)

    return [item[:4] for item in backups]


def is_valid_backup(path):
    """Check that a file is a healthy database made by this app."""

    if not os.path.isfile(path):
        return False, "File not found."

    conn = None

    try:
        conn = sqlite3.connect(path)

        result = conn.execute("PRAGMA integrity_check").fetchone()
        if result is None or result[0] != "ok":
            return False, "The file is damaged."

        tables = {
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

        if not REQUIRED_TABLES.issubset(tables):
            return False, "This is not a backup of this application."

        return True, "OK"

    except sqlite3.DatabaseError:
        return False, "This file is not a valid database."

    finally:
        if conn is not None:
            conn.close()


def restore_backup(path):
    """Replace current data with a backup. Returns (success, message)."""

    valid, message = is_valid_backup(path)
    if not valid:
        return False, message

    # Safety copy of the current data, in case the restore is a mistake
    saved, save_message, _ = create_backup("before_restore")
    if not saved:
        return False, "Restore cancelled. " + save_message

    source = None
    target = None

    try:
        source = sqlite3.connect(path)
        target = get_connection()
        source.backup(target)
        return True, "Database restored successfully."

    except Exception as error:
        return False, f"Restore failed: {error}"

    finally:
        if source is not None:
            source.close()
        if target is not None:
            target.close()