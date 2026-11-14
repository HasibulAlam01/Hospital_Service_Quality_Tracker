# Hospital Service Quality and Neglect Tracker

A desktop application where patients can submit complaints about hospital
services and administrators can track, update and report on them.

## Features

- Patient registration and secure login (hashed passwords)
- Submit complaints by department, with optional photo or PDF attachment
- Patients can view the status history and admin remarks
- Admin dashboard: view and filter all complaints, change status, add remarks
- Reports: complaints per department and overdue complaints (over 7 days)
- Database backup and restore
- Works fully offline

## Technologies

Python, SQLite, CustomTkinter, PyInstaller

## How to run

1. Install Python 3.10 or newer.
2. Install the requirements:

       pip install -r requirements.txt

3. Start the app:

       python gui.py

## Default admin login

- Username: `admin`
- Password: `Admin@12345`

(Change this password before using the system for real.)

## Build the .exe (Windows)

    pyinstaller --noconfirm --onedir --windowed --name HospitalTracker --collect-all customtkinter gui.py

The program is created in `dist/HospitalTracker`.

## Project files

| File | Purpose |
|------|---------|
| `gui.py` | Main desktop application |
| `config.py` | Settings and folder paths |
| `database.py` | Creates the database tables |
| `auth.py` | Registration and login |
| `complaints.py` | Complaints and attachments |
| `admin.py` | Status changes and remarks |
| `reports.py`, `reports_screen.py` | Reports |
| `backup_restore.py`, `backup_screen.py` | Backup and restore |