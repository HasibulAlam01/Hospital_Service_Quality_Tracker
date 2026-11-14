import customtkinter as ctk
from tkinter import filedialog, messagebox

from config import BACKUP_DIR
from backup_restore import create_backup, list_backups, restore_backup


def show_backup_screen(app, user, message="", message_color="#157f3b"):
    """Draw the Backup and Restore page inside the admin layout."""

    content = app.build_admin_layout(user, "backup")

    ctk.CTkLabel(
        content, text="Backup and Restore",
        font=("Segoe UI", 24, "bold"), text_color="#1a2433"
    ).pack(pady=(30, 0), padx=30, anchor="w")

    ctk.CTkLabel(
        content,
        text="Save a copy of the database, or recover an earlier copy.",
        font=("Segoe UI", 13), text_color="#6b7789"
    ).pack(padx=30, anchor="w", pady=(0, 12))

    # ---------- Action buttons ----------
    actions = ctk.CTkFrame(content, fg_color="transparent")
    actions.pack(fill="x", padx=30)

    ctk.CTkButton(
        actions, text="Create backup now", width=170, height=38,
        command=lambda: do_create(app, user)
    ).pack(side="left")

    ctk.CTkButton(
        actions, text="Restore from file...", width=170, height=38,
        fg_color="#e8eef6", text_color="#0f6aa6", hover_color="#d6e2f0",
        command=lambda: do_restore_from_file(app, user)
    ).pack(side="left", padx=10)

    ctk.CTkLabel(
        content, text=message, font=("Segoe UI", 13),
        text_color=message_color, wraplength=700, justify="left"
    ).pack(padx=30, anchor="w", pady=(10, 0))

    # ---------- Saved backups ----------
    ctk.CTkLabel(
        content, text="Saved backups",
        font=("Segoe UI", 16, "bold"), text_color="#1a2433"
    ).pack(padx=30, anchor="w", pady=(12, 6))

    backups = list_backups()

    if not backups:
        ctk.CTkLabel(
            content, text="No backups yet. Click 'Create backup now'.",
            font=("Segoe UI", 13), text_color="#6b7789"
        ).pack(padx=30, anchor="w")
        return

    table = ctk.CTkScrollableFrame(
        content, width=700, height=280, fg_color="white")
    table.pack(padx=30, anchor="w")

    widths = [330, 70, 140, 80]
    headers = ["File", "Size", "Created", ""]

    for col, (text, width) in enumerate(zip(headers, widths)):
        ctk.CTkLabel(
            table, text=text, width=width, anchor="w",
            font=("Segoe UI", 12, "bold"), text_color="#6b7789"
        ).grid(row=0, column=col, padx=4, pady=(6, 8))

    for r, (name, path, size_kb, modified) in enumerate(backups, start=1):
        values = [name, f"{size_kb} KB", modified]

        for col, (text, width) in enumerate(zip(values, widths)):
            ctk.CTkLabel(
                table, text=text, width=width, anchor="w",
                font=("Segoe UI", 12), text_color="#1a2433"
            ).grid(row=r, column=col, padx=4, pady=5)

        ctk.CTkButton(
            table, text="Restore", width=70, height=28,
            fg_color="#b54708", hover_color="#93390a",
            command=lambda p=path: confirm_restore(app, user, p)
        ).grid(row=r, column=3, padx=4, pady=5)


def do_create(app, user):
    ok, message, _ = create_backup()
    show_backup_screen(
        app, user, message, "#157f3b" if ok else "#b42318")


def do_restore_from_file(app, user):
    path = filedialog.askopenfilename(
        title="Choose a backup file",
        initialdir=BACKUP_DIR,
        filetypes=[("Database backup", "*.db")]
    )
    if path:
        confirm_restore(app, user, path)


def confirm_restore(app, user, path):
    answer = messagebox.askyesno(
        "Restore backup",
        "This will replace ALL current data with the selected backup.\n\n"
        "A safety copy of the current data will be saved first.\n\n"
        "Do you want to continue?"
    )
    if not answer:
        return

    ok, message = restore_backup(path)

    if ok:
        messagebox.showinfo(
            "Restore complete",
            message + "\n\nYou will now be logged out. "
                      "Please log in again."
        )
        app.logout()
    else:
        show_backup_screen(app, user, message, "#b42318")