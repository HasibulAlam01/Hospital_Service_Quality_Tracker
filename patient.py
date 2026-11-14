import tkinter as tk
from tkinter import ttk, messagebox

from database import get_connection


BG_COLOR = "#F1F5F9"
DARK_COLOR = "#164E63"


def show_patient_dashboard(root, user, logout_callback):

    # Clear the previous screen
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg=BG_COLOR)

    # Header
    header = tk.Frame(root, bg=DARK_COLOR, height=100)
    header.pack(fill="x")

    tk.Label(
        header,
        text="HOSPITAL SERVICE QUALITY",
        font=("Arial", 20, "bold"),
        fg="white",
        bg=DARK_COLOR
    ).pack(pady=(20, 5))

    tk.Label(
        header,
        text="PATIENT DASHBOARD",
        font=("Arial", 11),
        fg="white",
        bg=DARK_COLOR
    ).pack()

    # Main area
    main = tk.Frame(root, bg=BG_COLOR)
    main.pack(fill="both", expand=True, padx=40, pady=20)

    tk.Label(
        main,
        text="Welcome, " + user["full_name"] + "!",
        font=("Arial", 20, "bold"),
        fg=DARK_COLOR,
        bg=BG_COLOR
    ).pack(pady=10)

    tk.Label(
        main,
        text="Submit a Hospital Complaint",
        font=("Arial", 15, "bold"),
        bg=BG_COLOR
    ).pack(pady=10)

    form = tk.Frame(main, bg=BG_COLOR)
    form.pack()

    # Department
    tk.Label(
        form,
        text="Select Department",
        font=("Arial", 11, "bold"),
        bg=BG_COLOR
    ).grid(row=0, column=0, sticky="w", pady=6)

    department_box = ttk.Combobox(
        form,
        width=42,
        state="readonly"
    )
    department_box.grid(row=1, column=0, pady=(0, 12))

    # Load departments from database
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT department_name
        FROM departments
        WHERE is_active = 1
        ORDER BY department_name
    """)

    departments = [row[0] for row in cursor.fetchall()]
    conn.close()

    department_box["values"] = departments

    if departments:
        department_box.current(0)

    # Subject
    tk.Label(
        form,
        text="Complaint Subject",
        font=("Arial", 11, "bold"),
        bg=BG_COLOR
    ).grid(row=2, column=0, sticky="w", pady=6)

    subject_entry = ttk.Entry(form, width=45)
    subject_entry.grid(row=3, column=0, pady=(0, 12))

    # Description
    tk.Label(
        form,
        text="Complaint Description",
        font=("Arial", 11, "bold"),
        bg=BG_COLOR
    ).grid(row=4, column=0, sticky="w", pady=6)

    description_box = tk.Text(
        form,
        width=45,
        height=6,
        font=("Arial", 11)
    )
    description_box.grid(row=5, column=0, pady=(0, 15))

    # Submit complaint
    def submit_complaint():

        department = department_box.get()
        subject = subject_entry.get().strip()
        description = description_box.get(
            "1.0", "end"
        ).strip()

        if not department or not subject or not description:
            messagebox.showwarning(
                "Missing Information",
                "Please complete all complaint fields."
            )
            return

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT department_id
                FROM departments
                WHERE department_name = ?
            """, (department,))

            department_result = cursor.fetchone()

            if department_result is None:
                messagebox.showerror(
                    "Error",
                    "Selected department was not found."
                )
                return

            department_id = department_result[0]

            cursor.execute("""
                INSERT INTO complaints (
                    user_id,
                    department_id,
                    subject,
                    description
                )
                VALUES (?, ?, ?, ?)
            """, (
                user["user_id"],
                department_id,
                subject,
                description
            ))

            conn.commit()

            complaint_id = cursor.lastrowid

            messagebox.showinfo(
                "Complaint Submitted",
                f"Your complaint was submitted successfully!\n"
                f"Complaint ID: {complaint_id}\n"
                f"Status: Pending"
            )

            subject_entry.delete(0, "end")
            description_box.delete("1.0", "end")

        except Exception as error:
            messagebox.showerror(
                "Submission Error",
                str(error)
            )

        finally:
            conn.close()

    ttk.Button(
        form,
        text="SUBMIT COMPLAINT",
        command=submit_complaint
    ).grid(row=6, column=0, sticky="ew", pady=8)

    ttk.Button(
        main,
        text="LOGOUT",
        command=logout_callback
    ).pack(pady=12)