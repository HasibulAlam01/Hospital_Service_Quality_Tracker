import os
import customtkinter as ctk
from tkinter import filedialog

from config import APP_NAME, ATTACHMENT_DIR
from database import create_tables
from reports_screen import show_reports_screen
from backup_screen import show_backup_screen
from auth import (
    create_default_admin,
    authenticate_user,
    create_staff_account,
    list_staff_accounts,
)
from complaints import (
    get_departments,
    submit_complaint,
    get_staff_complaints,
    get_all_complaints,
    get_complaint_detail,
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

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

STATUS_COLORS = {
    "Pending": "#b54708",
    "In Progress": "#0f6aa6",
    "Resolved": "#157f3b",
}


class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1000x600")
        self.resizable(False, False)
        self.selected_file = None
        self.show_login()

    def clear(self):
        """Remove everything from the window."""
        for widget in self.winfo_children():
            widget.destroy()

    def build_split_background(self):
        """Dark left panel and light right panel. Returns the right panel."""
        left = ctk.CTkFrame(self, width=500, height=600,
                            corner_radius=0, fg_color="#101b2b")
        left.place(x=0, y=0)

        ctk.CTkLabel(
            left, text="Hospital Service\nQuality Tracker",
            font=("Segoe UI", 32, "bold"),
            text_color="white", justify="left"
        ).place(x=50, y=190)

        ctk.CTkLabel(
            left,
            text="Record patient complaints, track their progress\n"
                 "and help improve hospital care.",
            font=("Segoe UI", 15),
            text_color="#b8c4d6", justify="left"
        ).place(x=50, y=300)

        right = ctk.CTkFrame(self, width=500, height=600,
                             corner_radius=0, fg_color="#f4f6f9")
        right.place(x=500, y=0)
        return right

    # ================= Login screen =================

    def show_login(self):
        self.clear()
        self.configure(fg_color=("gray92", "gray14"))
        right = self.build_split_background()

        box = ctk.CTkFrame(right, width=380, height=400,
                           fg_color="white", corner_radius=12)
        box.place(x=60, y=100)
        box.pack_propagate(False)

        ctk.CTkLabel(
            box, text="Welcome back",
            font=("Segoe UI", 24, "bold"), text_color="#1a2433"
        ).pack(pady=(30, 0), padx=30, anchor="w")

        ctk.CTkLabel(
            box, text="Sign in to your account",
            font=("Segoe UI", 13), text_color="#6b7789"
        ).pack(padx=30, anchor="w")

        ctk.CTkLabel(
            box, text="Username", font=("Segoe UI", 13, "bold"),
            text_color="#1a2433"
        ).pack(pady=(20, 4), padx=30, anchor="w")

        self.username_entry = ctk.CTkEntry(
            box, width=320, height=40,
            placeholder_text="Enter your username"
        )
        self.username_entry.pack(padx=30)

        ctk.CTkLabel(
            box, text="Password", font=("Segoe UI", 13, "bold"),
            text_color="#1a2433"
        ).pack(pady=(14, 4), padx=30, anchor="w")

        self.password_entry = ctk.CTkEntry(
            box, width=320, height=40, show="*",
            placeholder_text="Enter your password"
        )
        self.password_entry.pack(padx=30)

        self.message_label = ctk.CTkLabel(
            box, text="", font=("Segoe UI", 12), text_color="#b42318"
        )
        self.message_label.pack(pady=(10, 0))

        ctk.CTkButton(
            box, text="Sign In", width=320, height=42,
            font=("Segoe UI", 15, "bold"),
            command=self.do_login
        ).pack(pady=(6, 0), padx=30)

        ctk.CTkLabel(
            box, text="Staff accounts are created by the administrator.",
            font=("Segoe UI", 12), text_color="#6b7789"
        ).pack(pady=(14, 0))

        self.bind("<Return>", lambda event: self.do_login())

    def do_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username.strip() or not password:
            self.message_label.configure(
                text="Please enter username and password.")
            return

        user = authenticate_user(username, password)

        if user is None:
            self.message_label.configure(
                text="Wrong username or password.")
            return

        self.unbind("<Return>")
        self.show_dashboard(user)

    # ================= After login =================

    def show_dashboard(self, user):
        if user["role"] == "admin":
            self.show_admin_complaints(user)
        else:
            self.show_register_complaint(user)

    def logout(self):
        self.selected_file = None
        self.show_login()

    # ================= Shared sidebar =================

    def build_layout(self, user, menu_items, active):
        """Sidebar on the left. menu_items = [(key, text, command)].
        Returns the content area on the right."""
        self.clear()
        self.configure(fg_color="#f4f6f9")

        sidebar = ctk.CTkFrame(self, width=220, height=600,
                               corner_radius=0, fg_color="#101b2b")
        sidebar.place(x=0, y=0)
        sidebar.pack_propagate(False)

        ctk.CTkLabel(
            sidebar, text="Hospital Service\nQuality Tracker",
            font=("Segoe UI", 17, "bold"),
            text_color="white", justify="left"
        ).pack(pady=(30, 4), padx=20, anchor="w")

        ctk.CTkLabel(
            sidebar, text=user["full_name"][:24],
            font=("Segoe UI", 12), text_color="#8fc3ff"
        ).pack(padx=20, anchor="w")

        ctk.CTkLabel(
            sidebar, text=user["role"].capitalize(),
            font=("Segoe UI", 11), text_color="#6b7f9c"
        ).pack(padx=20, anchor="w", pady=(0, 26))

        for key, text, command in menu_items:
            ctk.CTkButton(
                sidebar, text="  " + text, width=190, height=40,
                anchor="w", font=("Segoe UI", 14),
                fg_color="#1e3350" if key == active else "transparent",
                hover_color="#1e3350", text_color="white",
                command=command
            ).pack(padx=15, pady=3)

        ctk.CTkButton(
            sidebar, text="Logout", width=190, height=40,
            fg_color="#2a3b55", hover_color="#b42318",
            command=self.logout
        ).pack(side="bottom", pady=25)

        content = ctk.CTkFrame(self, width=780, height=600,
                               corner_radius=0, fg_color="#f4f6f9")
        content.place(x=220, y=0)
        content.pack_propagate(False)
        return content

    def build_staff_layout(self, user, active):
        return self.build_layout(user, [
            ("register", "Register Complaint",
             lambda: self.show_register_complaint(user)),
            ("complaints", "Recorded Complaints",
             lambda: self.show_staff_complaints(user)),
        ], active)

    def build_admin_layout(self, user, active):
        return self.build_layout(user, [
            ("all", "All Complaints",
             lambda: self.show_admin_complaints(user)),
            ("reports", "Reports",
             lambda: show_reports_screen(self, user)),
            ("staff", "Manage Staff",
             lambda: self.show_manage_staff(user)),
            ("backup", "Backup and Restore",
             lambda: show_backup_screen(self, user)),
        ], active)

    # ================= Shared: complaint details block =================

    def fill_details(self, scroll, detail, complaint_id):
        """Fill a scrollable frame with everything about one complaint."""
        (_, patient, phone, ward, dept, subject, description,
         status, date, recorder) = detail

        def title(text):
            ctk.CTkLabel(
                scroll, text=text, font=("Segoe UI", 15, "bold"),
                text_color="#1a2433"
            ).pack(anchor="w", padx=12, pady=(12, 4))

        def line(text, color="#3b4658"):
            ctk.CTkLabel(
                scroll, text=text, font=("Segoe UI", 13),
                text_color=color, justify="left",
                wraplength=640, anchor="w"
            ).pack(anchor="w", padx=22, pady=1)

        title(subject)
        line(f"Patient: {patient}    Phone: {phone or 'Not given'}")
        line(f"Ward / Bed: {ward or 'Not given'}")
        line(f"Department: {dept}")
        line(f"Recorded by: {recorder}    Date: {date}")
        line(f"Current status: {status}",
             STATUS_COLORS.get(status, "#3b4658"))

        title("Description")
        line(description)

        title("Attachments")
        attachments = get_attachments(complaint_id)
        if not attachments:
            line("No attachments.", "#6b7789")
        for _, name, stored, ftype, when in attachments:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(anchor="w", padx=22, pady=2)
            ctk.CTkLabel(
                row, text=f"{name}  ({ftype})  uploaded {when}",
                font=("Segoe UI", 13), text_color="#3b4658"
            ).pack(side="left")
            ctk.CTkButton(
                row, text="Open file", width=80, height=26,
                command=lambda s=stored: self.open_attachment(s)
            ).pack(side="left", padx=10)

        title("Status history")
        for old, new, who, when in get_status_history(complaint_id):
            line(f"{when}:  {old or 'New'}  ->  {new}   (by {who})")

        title("Remarks from hospital management")
        remarks = get_remarks(complaint_id)
        if not remarks:
            line("No remarks yet.", "#6b7789")
        for _, who, text, when in remarks:
            line(f"{when} - {who}:\n{text}")

    def open_attachment(self, stored_name):
        path = os.path.join(ATTACHMENT_DIR, stored_name)
        if os.path.isfile(path):
            os.startfile(path)

    # ================= Staff: register complaint =================

    def show_register_complaint(self, user, message="",
                                message_color="#157f3b"):
        content = self.build_staff_layout(user, "register")
        self.selected_file = None

        ctk.CTkLabel(
            content, text="Register a Complaint",
            font=("Segoe UI", 24, "bold"), text_color="#1a2433"
        ).pack(pady=(22, 0), padx=30, anchor="w")

        ctk.CTkLabel(
            content,
            text="Record the problem reported by a patient or attendant.",
            font=("Segoe UI", 13), text_color="#6b7789"
        ).pack(padx=30, anchor="w", pady=(0, 8))

        self.departments = get_departments()
        self.dept_map = {name: dept_id for dept_id, name in self.departments}

        label_font = ("Segoe UI", 13, "bold")

        # Row 1: patient name and phone
        row1 = ctk.CTkFrame(content, fg_color="transparent")
        row1.pack(padx=30, anchor="w")

        col = ctk.CTkFrame(row1, fg_color="transparent")
        col.pack(side="left")
        ctk.CTkLabel(col, text="Patient name *", font=label_font,
                     text_color="#1a2433").pack(anchor="w")
        self.patient_name_entry = ctk.CTkEntry(
            col, width=340, height=36, placeholder_text="Full name")
        self.patient_name_entry.pack(pady=(2, 8))

        col = ctk.CTkFrame(row1, fg_color="transparent")
        col.pack(side="left", padx=(20, 0))
        ctk.CTkLabel(col, text="Patient phone", font=label_font,
                     text_color="#1a2433").pack(anchor="w")
        self.patient_phone_entry = ctk.CTkEntry(
            col, width=340, height=36, placeholder_text="Optional")
        self.patient_phone_entry.pack(pady=(2, 8))

        # Row 2: ward/bed and department
        row2 = ctk.CTkFrame(content, fg_color="transparent")
        row2.pack(padx=30, anchor="w")

        col = ctk.CTkFrame(row2, fg_color="transparent")
        col.pack(side="left")
        ctk.CTkLabel(col, text="Ward / Bed", font=label_font,
                     text_color="#1a2433").pack(anchor="w")
        self.ward_entry = ctk.CTkEntry(
            col, width=340, height=36, placeholder_text="Optional")
        self.ward_entry.pack(pady=(2, 8))

        col = ctk.CTkFrame(row2, fg_color="transparent")
        col.pack(side="left", padx=(20, 0))
        ctk.CTkLabel(col, text="Department *", font=label_font,
                     text_color="#1a2433").pack(anchor="w")
        self.dept_menu = ctk.CTkOptionMenu(
            col, values=list(self.dept_map.keys()), width=340, height=36)
        self.dept_menu.pack(pady=(2, 8))

        # Subject
        ctk.CTkLabel(
            content, text="Subject *", font=label_font,
            text_color="#1a2433"
        ).pack(padx=30, anchor="w")

        self.subject_entry = ctk.CTkEntry(
            content, width=700, height=36,
            placeholder_text="Short title of the problem")
        self.subject_entry.pack(padx=30, anchor="w", pady=(2, 8))

        # Description
        ctk.CTkLabel(
            content, text="Description *", font=label_font,
            text_color="#1a2433"
        ).pack(padx=30, anchor="w")

        self.description_box = ctk.CTkTextbox(
            content, width=700, height=85,
            fg_color="white", border_width=1, border_color="#d3dae5")
        self.description_box.pack(padx=30, anchor="w", pady=(2, 8))

        # Attachment
        file_row = ctk.CTkFrame(content, fg_color="transparent")
        file_row.pack(padx=30, anchor="w")

        ctk.CTkButton(
            file_row, text="Choose file (optional)", width=170, height=32,
            fg_color="#e8eef6", text_color="#0f6aa6",
            hover_color="#d6e2f0",
            command=self.choose_file
        ).pack(side="left")

        self.file_label = ctk.CTkLabel(
            file_row, text="No file selected  (JPG, PNG or PDF, max 5 MB)",
            font=("Segoe UI", 12), text_color="#6b7789")
        self.file_label.pack(side="left", padx=12)

        # Submit button and message on one row
        bottom = ctk.CTkFrame(content, fg_color="transparent")
        bottom.pack(padx=30, anchor="w", pady=(10, 0))

        ctk.CTkButton(
            bottom, text="Register Complaint", width=220, height=40,
            font=("Segoe UI", 15, "bold"),
            command=lambda: self.do_submit(user)
        ).pack(side="left")

        self.submit_message = ctk.CTkLabel(
            bottom, text=message, font=("Segoe UI", 13),
            text_color=message_color)
        self.submit_message.pack(side="left", padx=14)

    def choose_file(self):
        path = filedialog.askopenfilename(
            title="Choose a file",
            filetypes=[("Images and PDF", "*.jpg *.jpeg *.png *.pdf")]
        )
        if path:
            self.selected_file = path
            self.file_label.configure(text=os.path.basename(path))

    def do_submit(self, user):
        dept_id = self.dept_map[self.dept_menu.get()]

        ok, message, complaint_id = submit_complaint(
            user["user_id"],
            dept_id,
            self.patient_name_entry.get(),
            self.patient_phone_entry.get(),
            self.ward_entry.get(),
            self.subject_entry.get(),
            self.description_box.get("1.0", "end"),
        )

        if not ok:
            self.submit_message.configure(
                text=message, text_color="#b42318")
            return

        if self.selected_file:
            file_ok, file_message = save_attachment(
                complaint_id, self.selected_file)
            if not file_ok:
                message += "  (File not attached: " + file_message + ")"
                self.show_register_complaint(user, message, "#b54708")
                return

        self.show_register_complaint(user, message, "#157f3b")

    # ================= Staff: recorded complaints =================

    def show_staff_complaints(self, user):
        content = self.build_staff_layout(user, "complaints")

        ctk.CTkLabel(
            content, text="Recorded Complaints",
            font=("Segoe UI", 24, "bold"), text_color="#1a2433"
        ).pack(pady=(30, 0), padx=30, anchor="w")

        ctk.CTkLabel(
            content,
            text="Complaints you recorded. Click View for remarks "
                 "and progress.",
            font=("Segoe UI", 13), text_color="#6b7789"
        ).pack(padx=30, anchor="w", pady=(0, 12))

        rows = get_staff_complaints(user["user_id"])

        if not rows:
            ctk.CTkLabel(
                content, text="You have not recorded any complaints yet.",
                font=("Segoe UI", 14), text_color="#6b7789"
            ).pack(padx=30, anchor="w", pady=20)
            return

        table = ctk.CTkScrollableFrame(
            content, width=700, height=420, fg_color="white")
        table.pack(padx=30, anchor="w")

        widths = [35, 110, 95, 170, 85, 100, 65]
        headers = ["ID", "Patient", "Department", "Subject",
                   "Status", "Date", ""]

        for col, (text, width) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(
                table, text=text, width=width, anchor="w",
                font=("Segoe UI", 12, "bold"), text_color="#6b7789"
            ).grid(row=0, column=col, padx=3, pady=(6, 8))

        for r, (cid, patient, dept, subject, status, date) in enumerate(
                rows, start=1):
            values = [str(cid), patient[:14], dept, subject[:22],
                      status, date[:10]]

            for col, (text, width) in enumerate(zip(values, widths)):
                color = "#1a2433"
                if col == 4:
                    color = STATUS_COLORS.get(status, "#1a2433")
                ctk.CTkLabel(
                    table, text=text, width=width, anchor="w",
                    font=("Segoe UI", 12,
                          "bold" if col == 4 else "normal"),
                    text_color=color
                ).grid(row=r, column=col, padx=3, pady=6)

            ctk.CTkButton(
                table, text="View", width=55, height=28,
                command=lambda c=cid: self.show_staff_details(user, c)
            ).grid(row=r, column=6, padx=3, pady=6)

    # ================= Staff: complaint details =================

    def show_staff_details(self, user, complaint_id,
                           message="", message_color="#157f3b"):
        content = self.build_staff_layout(user, "complaints")

        # Staff can only open complaints they recorded
        my_ids = [row[0] for row in get_staff_complaints(user["user_id"])]
        detail = get_complaint_detail(complaint_id)

        if complaint_id not in my_ids or detail is None:
            self.show_staff_complaints(user)
            return

        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(fill="x", padx=30, pady=(25, 0))

        ctk.CTkButton(
            top, text="< Back", width=70, height=30,
            fg_color="#e8eef6", text_color="#0f6aa6",
            hover_color="#d6e2f0",
            command=lambda: self.show_staff_complaints(user)
        ).pack(side="left")

        ctk.CTkLabel(
            top, text=f"Complaint #{complaint_id}",
            font=("Segoe UI", 22, "bold"), text_color="#1a2433"
        ).pack(side="left", padx=15)

        scroll = ctk.CTkScrollableFrame(
            content, width=700, height=400, fg_color="white")
        scroll.pack(padx=30, pady=(12, 0), anchor="w")

        self.fill_details(scroll, detail, complaint_id)

        bottom = ctk.CTkFrame(content, fg_color="transparent")
        bottom.pack(fill="x", padx=30, pady=(10, 0))

        ctk.CTkButton(
            bottom, text="Attach a file", width=140, height=34,
            command=lambda: self.attach_to_complaint(user, complaint_id)
        ).pack(side="left")

        ctk.CTkLabel(
            bottom, text=message, font=("Segoe UI", 12),
            text_color=message_color
        ).pack(side="left", padx=12)

    def attach_to_complaint(self, user, complaint_id):
        path = filedialog.askopenfilename(
            title="Choose a file",
            filetypes=[("Images and PDF", "*.jpg *.jpeg *.png *.pdf")]
        )
        if not path:
            return

        ok, message = save_attachment(complaint_id, path)
        self.show_staff_details(
            user, complaint_id, message,
            "#157f3b" if ok else "#b42318"
        )

    # ================= Admin: all complaints =================

    def show_admin_complaints(self, user, status_filter="All"):
        content = self.build_admin_layout(user, "all")

        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(fill="x", padx=30, pady=(30, 0))

        ctk.CTkLabel(
            top, text="All Complaints",
            font=("Segoe UI", 24, "bold"), text_color="#1a2433"
        ).pack(side="left")

        filter_menu = ctk.CTkOptionMenu(
            top, values=["All"] + VALID_STATUSES, width=140, height=32,
            command=lambda value: self.show_admin_complaints(user, value)
        )
        filter_menu.set(status_filter)
        filter_menu.pack(side="right")

        ctk.CTkLabel(
            top, text="Filter:", font=("Segoe UI", 13),
            text_color="#6b7789"
        ).pack(side="right", padx=8)

        rows = get_all_complaints()
        if status_filter != "All":
            rows = [r for r in rows if r[4] == status_filter]

        ctk.CTkLabel(
            content, text=f"{len(rows)} complaint(s)",
            font=("Segoe UI", 13), text_color="#6b7789"
        ).pack(padx=30, anchor="w", pady=(2, 10))

        if not rows:
            ctk.CTkLabel(
                content, text="No complaints found.",
                font=("Segoe UI", 14), text_color="#6b7789"
            ).pack(padx=30, anchor="w", pady=20)
            return

        table = ctk.CTkScrollableFrame(
            content, width=700, height=410, fg_color="white")
        table.pack(padx=30, anchor="w")

        widths = [35, 110, 95, 170, 85, 100, 65]
        headers = ["ID", "Patient", "Department", "Subject",
                   "Status", "Date", ""]

        for col, (text, width) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(
                table, text=text, width=width, anchor="w",
                font=("Segoe UI", 12, "bold"), text_color="#6b7789"
            ).grid(row=0, column=col, padx=3, pady=(6, 8))

        for r, (cid, patient, dept, subject, status, date) in enumerate(
                rows, start=1):
            values = [str(cid), patient[:14], dept, subject[:22],
                      status, date[:10]]

            for col, (text, width) in enumerate(zip(values, widths)):
                color = "#1a2433"
                if col == 4:
                    color = STATUS_COLORS.get(status, "#1a2433")
                ctk.CTkLabel(
                    table, text=text, width=width, anchor="w",
                    font=("Segoe UI", 12,
                          "bold" if col == 4 else "normal"),
                    text_color=color
                ).grid(row=r, column=col, padx=3, pady=6)

            ctk.CTkButton(
                table, text="View", width=55, height=28,
                command=lambda c=cid: self.show_admin_details(user, c)
            ).grid(row=r, column=6, padx=3, pady=6)

    # ================= Admin: complaint details =================

    def show_admin_details(self, user, complaint_id,
                           message="", message_color="#157f3b"):
        content = self.build_admin_layout(user, "all")

        detail = get_complaint_detail(complaint_id)
        if detail is None:
            self.show_admin_complaints(user)
            return

        status = detail[7]

        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(fill="x", padx=30, pady=(20, 0))

        ctk.CTkButton(
            top, text="< Back", width=70, height=30,
            fg_color="#e8eef6", text_color="#0f6aa6",
            hover_color="#d6e2f0",
            command=lambda: self.show_admin_complaints(user)
        ).pack(side="left")

        ctk.CTkLabel(
            top, text=f"Complaint #{complaint_id}",
            font=("Segoe UI", 22, "bold"), text_color="#1a2433"
        ).pack(side="left", padx=15)

        # Action bar: change status
        actions = ctk.CTkFrame(content, fg_color="white", corner_radius=8)
        actions.pack(fill="x", padx=30, pady=(10, 0))

        ctk.CTkLabel(
            actions, text="Change status:", font=("Segoe UI", 13, "bold"),
            text_color="#1a2433"
        ).pack(side="left", padx=(12, 6), pady=8)

        status_menu = ctk.CTkOptionMenu(
            actions, values=VALID_STATUSES, width=130, height=32)
        status_menu.set(status)
        status_menu.pack(side="left", pady=8)

        ctk.CTkButton(
            actions, text="Update", width=80, height=32,
            command=lambda: self.do_update_status(
                user, complaint_id, status_menu.get())
        ).pack(side="left", padx=8, pady=8)

        ctk.CTkLabel(
            actions, text=message, font=("Segoe UI", 12),
            text_color=message_color
        ).pack(side="left", padx=8)

        # Details
        scroll = ctk.CTkScrollableFrame(
            content, width=700, height=290, fg_color="white")
        scroll.pack(padx=30, pady=(10, 0), anchor="w")

        self.fill_details(scroll, detail, complaint_id)

        # Add remark
        remark_row = ctk.CTkFrame(content, fg_color="transparent")
        remark_row.pack(fill="x", padx=30, pady=(10, 0))

        remark_entry = ctk.CTkEntry(
            remark_row, width=560, height=36,
            placeholder_text="Write a remark for this complaint...")
        remark_entry.pack(side="left")

        ctk.CTkButton(
            remark_row, text="Add remark", width=120, height=36,
            command=lambda: self.do_add_remark(
                user, complaint_id, remark_entry.get())
        ).pack(side="left", padx=10)

    def do_update_status(self, user, complaint_id, new_status):
        ok, message = update_status(
            complaint_id, new_status, user["user_id"])
        self.show_admin_details(
            user, complaint_id, message,
            "#157f3b" if ok else "#b42318"
        )

    def do_add_remark(self, user, complaint_id, text):
        ok, message = add_remark(complaint_id, user["user_id"], text)
        self.show_admin_details(
            user, complaint_id, message,
            "#157f3b" if ok else "#b42318"
        )

    # ================= Admin: manage staff =================

    def show_manage_staff(self, user, message="", message_color="#157f3b"):
        content = self.build_admin_layout(user, "staff")

        ctk.CTkLabel(
            content, text="Manage Staff",
            font=("Segoe UI", 24, "bold"), text_color="#1a2433"
        ).pack(pady=(25, 0), padx=30, anchor="w")

        ctk.CTkLabel(
            content,
            text="Create accounts for hospital staff who record complaints.",
            font=("Segoe UI", 13), text_color="#6b7789"
        ).pack(padx=30, anchor="w", pady=(0, 8))

        form = ctk.CTkFrame(content, fg_color="white", corner_radius=10)
        form.pack(padx=30, anchor="w")

        def entry(parent, placeholder, show=None):
            e = ctk.CTkEntry(parent, width=330, height=36,
                             placeholder_text=placeholder, show=show)
            return e

        row1 = ctk.CTkFrame(form, fg_color="transparent")
        row1.pack(padx=14, pady=(12, 0))
        self.st_name = entry(row1, "Full name *")
        self.st_name.pack(side="left", padx=(0, 10))
        self.st_username = entry(row1, "Username *")
        self.st_username.pack(side="left")

        row2 = ctk.CTkFrame(form, fg_color="transparent")
        row2.pack(padx=14, pady=(8, 0))
        self.st_email = entry(row2, "Email (optional)")
        self.st_email.pack(side="left", padx=(0, 10))
        self.st_phone = entry(row2, "Phone (optional)")
        self.st_phone.pack(side="left")

        row3 = ctk.CTkFrame(form, fg_color="transparent")
        row3.pack(padx=14, pady=(8, 0))
        self.st_password = entry(
            row3, "Password (at least 8 characters) *", show="*")
        self.st_password.pack(side="left", padx=(0, 10))
        self.st_confirm = entry(row3, "Confirm password *", show="*")
        self.st_confirm.pack(side="left")

        row4 = ctk.CTkFrame(form, fg_color="transparent")
        row4.pack(padx=14, pady=(10, 12), anchor="w")
        ctk.CTkButton(
            row4, text="Create staff account", width=200, height=36,
            command=lambda: self.do_create_staff(user)
        ).pack(side="left")
        self.staff_message = ctk.CTkLabel(
            row4, text=message, font=("Segoe UI", 12),
            text_color=message_color)
        self.staff_message.pack(side="left", padx=12)

        ctk.CTkLabel(
            content, text="Existing staff accounts",
            font=("Segoe UI", 15, "bold"), text_color="#1a2433"
        ).pack(padx=30, anchor="w", pady=(12, 4))

        rows = list_staff_accounts()

        if not rows:
            ctk.CTkLabel(
                content, text="No staff accounts yet.",
                font=("Segoe UI", 13), text_color="#6b7789"
            ).pack(padx=30, anchor="w")
            return

        table = ctk.CTkScrollableFrame(
            content, width=700, height=170, fg_color="white")
        table.pack(padx=30, anchor="w")

        widths = [40, 200, 140, 130, 130]
        headers = ["ID", "Name", "Username", "Phone", "Created"]

        for col, (text, width) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(
                table, text=text, width=width, anchor="w",
                font=("Segoe UI", 12, "bold"), text_color="#6b7789"
            ).grid(row=0, column=col, padx=3, pady=(6, 6))

        for r, (uid, name, username, phone, created) in enumerate(
                rows, start=1):
            values = [str(uid), name[:26], username, phone or "-",
                      created[:10]]
            for col, (text, width) in enumerate(zip(values, widths)):
                ctk.CTkLabel(
                    table, text=text, width=width, anchor="w",
                    font=("Segoe UI", 12), text_color="#1a2433"
                ).grid(row=r, column=col, padx=3, pady=4)

    def do_create_staff(self, user):
        password = self.st_password.get()

        if password != self.st_confirm.get():
            self.staff_message.configure(
                text="Passwords do not match.", text_color="#b42318")
            return

        ok, message = create_staff_account(
            self.st_name.get(),
            self.st_username.get(),
            self.st_email.get(),
            self.st_phone.get(),
            password
        )

        if ok:
            self.show_manage_staff(user, message, "#157f3b")
        else:
            self.staff_message.configure(
                text=message, text_color="#b42318")


if __name__ == "__main__":
    create_tables()
    create_default_admin()
    App().mainloop()