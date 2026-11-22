# Hospital Service Quality and Neglect Tracker

A desktop application for use inside a hospital. Hospital staff record
complaints reported by patients or attendants, and the administrator tracks,
updates and reports on them, so that no complaint is neglected.

## Users

- **Admin (hospital management):** views and filters all complaints, changes
  status, adds remarks, creates staff accounts, views reports, and backs up
  and restores the database.
- **Staff (help desk, reception, nurses):** record a complaint for a patient
  (patient name, phone, ward/bed, department, subject, description, optional
  photo or PDF), and check the status and remarks of complaints they recorded.

There is no public registration. The admin creates staff accounts.

## Features

- Secure login with salted, hashed passwords (PBKDF2-SHA256)
- Staff record complaints with optional JPG, PNG or PDF attachment (max 5 MB)
- Admin changes status (Pending, In Progress, Resolved) and adds remarks
- Every status change is saved in a status history
- Reports: status counts, complaints per department, overdue complaints
  (not resolved after 7 days)
- Manage Staff: the admin creates staff accounts
- Database backup and restore, with a check of the backup file and a safety
  copy before restoring
- Works fully offline

## Technologies

Python, SQLite, CustomTkinter, PyInstaller

## Download the app (Windows)

Go to the **Releases** page of this repository, download `HospitalTracker.zip`,
right-click it, choose **Extract all**, then open `HospitalTracker.exe`.
Python is not needed.

## Run from source

1. Install Python 3.10 or newer.
2. Install the requirements:

       pip install -r requirements.txt

3. Start the app:

       python gui.py

## Default admin login

- Username: `admin`
- Password: `Admin@12345`

Log in as admin, open **Manage Staff**, and create a staff account. Then log
in with that staff account to record complaints. Change the default admin
password before real use.

## Build the .exe (Windows)

    pyinstaller --noconfirm --onedir --windowed --name HospitalTracker --collect-all customtkinter gui.py

The program is created in `dist/HospitalTracker`. The database and the
`attachments`, `backups` and `reports` folders are saved next to the .exe.

## Project files

| File | Purpose |
|------|---------|
| `gui.py` | Main desktop application (all screens) |
| `config.py` | Settings and folder paths |
| `database.py` | Creates the database tables |
| `auth.py` | Login, password hashing, staff accounts |
| `complaints.py` | Complaints and attachments |
| `admin.py` | Status changes and remarks |
| `reports.py`, `reports_screen.py` | Reports |
| `backup_restore.py`, `backup_screen.py` | Backup and restore |