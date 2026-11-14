from getpass import getpass

from config import APP_NAME
from database import create_tables
from auth import create_default_admin, register_patient, authenticate_user
from complaints import (
    get_departments,
    submit_complaint,
    get_patient_complaints,
    get_all_complaints,
    save_attachment,
    get_attachments,
)
from admin import (
    VALID_STATUSES,
    update_status,
    add_remark,
    get_remarks,
    get_status_history,
)


def ask_int(prompt):
    """Ask for a number. Returns None if the input is not a number."""
    try:
        return int(input(prompt).strip())
    except ValueError:
        print("Please enter a number.")
        return None


def show_patient_list(rows):
    if not rows:
        print("\nNo complaints found.")
        return
    print("\nID | Department | Subject | Status | Date")
    print("-" * 60)
    for cid, dept, subject, status, date in rows:
        print(f"{cid} | {dept} | {subject} | {status} | {date}")


def show_admin_list(rows):
    if not rows:
        print("\nNo complaints found.")
        return
    print("\nID | Patient | Department | Subject | Status | Date")
    print("-" * 70)
    for cid, name, dept, subject, status, date in rows:
        print(f"{cid} | {name} | {dept} | {subject} | {status} | {date}")


def show_details(complaint_id):
    """Show remarks, attachments and status history of a complaint."""
    print(f"\n--- Details of complaint {complaint_id} ---")

    print("\nStatus history:")
    for old, new, who, when in get_status_history(complaint_id):
        print(f"  {when}: {old or 'New'} -> {new} (by {who})")

    print("\nRemarks:")
    remarks = get_remarks(complaint_id)
    if not remarks:
        print("  No remarks yet.")
    for _, who, text, when in remarks:
        print(f"  {when} - {who}: {text}")

    print("\nAttachments:")
    attachments = get_attachments(complaint_id)
    if not attachments:
        print("  No attachments.")
    for _, name, _, ftype, when in attachments:
        print(f"  {name} ({ftype}) uploaded {when}")


# ---------------- Patient menu ----------------

def patient_submit(user):
    departments = get_departments()
    print("\nDepartments:")
    for dept_id, dept_name in departments:
        print(f"  {dept_id}. {dept_name}")

    dept_id = ask_int("Choose department number: ")
    if dept_id is None:
        return

    subject = input("Subject: ")
    description = input("Describe the problem: ")

    ok, message, complaint_id = submit_complaint(
        user["user_id"], dept_id, subject, description
    )
    print(message)

    if ok:
        path = input(
            "Attach a file? Type the file path, or press Enter to skip: "
        ).strip().strip('"')
        if path:
            print(save_attachment(complaint_id, path)[1])


def patient_attach(user):
    complaint_id = ask_int("Complaint ID: ")
    if complaint_id is None:
        return

    my_ids = [row[0] for row in get_patient_complaints(user["user_id"])]
    if complaint_id not in my_ids:
        print("That is not one of your complaints.")
        return

    path = input("File path: ").strip().strip('"')
    print(save_attachment(complaint_id, path)[1])


def patient_details(user):
    complaint_id = ask_int("Complaint ID: ")
    if complaint_id is None:
        return

    my_ids = [row[0] for row in get_patient_complaints(user["user_id"])]
    if complaint_id not in my_ids:
        print("That is not one of your complaints.")
        return

    show_details(complaint_id)


def patient_menu(user):
    while True:
        print(f"\n=== Patient Menu ({user['full_name']}) ===")
        print("1. Submit a complaint")
        print("2. My complaints")
        print("3. View complaint details")
        print("4. Attach a file to a complaint")
        print("5. Logout")

        choice = input("Choose: ").strip()

        if choice == "1":
            patient_submit(user)
        elif choice == "2":
            show_patient_list(get_patient_complaints(user["user_id"]))
        elif choice == "3":
            patient_details(user)
        elif choice == "4":
            patient_attach(user)
        elif choice == "5":
            break
        else:
            print("Invalid choice.")


# ---------------- Admin menu ----------------

def admin_change_status(user):
    complaint_id = ask_int("Complaint ID: ")
    if complaint_id is None:
        return

    print("Statuses:")
    for number, status in enumerate(VALID_STATUSES, start=1):
        print(f"  {number}. {status}")

    number = ask_int("Choose new status number: ")
    if number is None or not 1 <= number <= len(VALID_STATUSES):
        print("Invalid status number.")
        return

    print(update_status(
        complaint_id, VALID_STATUSES[number - 1], user["user_id"]
    )[1])


def admin_add_remark(user):
    complaint_id = ask_int("Complaint ID: ")
    if complaint_id is None:
        return

    text = input("Remark: ")
    print(add_remark(complaint_id, user["user_id"], text)[1])


def admin_details():
    complaint_id = ask_int("Complaint ID: ")
    if complaint_id is not None:
        show_details(complaint_id)


def admin_menu(user):
    while True:
        print(f"\n=== Admin Menu ({user['full_name']}) ===")
        print("1. View all complaints")
        print("2. View complaint details")
        print("3. Change complaint status")
        print("4. Add a remark")
        print("5. Logout")

        choice = input("Choose: ").strip()

        if choice == "1":
            show_admin_list(get_all_complaints())
        elif choice == "2":
            admin_details()
        elif choice == "3":
            admin_change_status(user)
        elif choice == "4":
            admin_add_remark(user)
        elif choice == "5":
            break
        else:
            print("Invalid choice.")


# ---------------- Start screen ----------------

def do_login():
    username = input("Username: ")
    password = getpass("Password (typing is hidden): ")

    user = authenticate_user(username, password)

    if user is None:
        print("Wrong username or password.")
    elif user["role"] == "admin":
        admin_menu(user)
    else:
        patient_menu(user)


def do_register():
    full_name = input("Full name: ")
    username = input("Username: ")
    email = input("Email (optional): ")
    phone = input("Phone (optional): ")
    password = getpass("Password, at least 8 characters (typing is hidden): ")

    print(register_patient(full_name, username, email, phone, password)[1])


def main():
    create_tables()
    create_default_admin()

    while True:
        print(f"\n===== {APP_NAME} =====")
        print("1. Login")
        print("2. Register as patient")
        print("3. Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            do_login()
        elif choice == "2":
            do_register()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()