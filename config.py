import os
import sys

# Main project folder.
# When running as an .exe, use the folder that contains the .exe,
# so the database and files are saved next to it.
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, "hospital_tracker.db")

# Application information
APP_NAME = "Hospital Service Quality and Neglect Tracker"

# File storage folder
ATTACHMENT_DIR = os.path.join(BASE_DIR, "attachments")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

# Create folders automatically if they do not exist
os.makedirs(ATTACHMENT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Complaint overdue period (days)
OVERDUE_DAYS = 7