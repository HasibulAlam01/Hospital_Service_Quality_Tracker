import customtkinter as ctk

from config import OVERDUE_DAYS
from reports import (
    get_status_counts,
    get_department_counts,
    get_overdue_complaints,
)


def show_reports_screen(app, user):
    """Draw the Reports page inside the admin layout."""

    content = app.build_admin_layout(user, "reports")

    ctk.CTkLabel(
        content, text="Reports",
        font=("Segoe UI", 24, "bold"), text_color="#1a2433"
    ).pack(pady=(30, 0), padx=30, anchor="w")

    ctk.CTkLabel(
        content, text="Overview of complaints and overdue cases.",
        font=("Segoe UI", 13), text_color="#6b7789"
    ).pack(padx=30, anchor="w", pady=(0, 10))

    scroll = ctk.CTkScrollableFrame(
        content, width=710, height=470, fg_color="transparent")
    scroll.pack(padx=20, anchor="w")

    status_counts = get_status_counts()
    overdue = get_overdue_complaints()
    total = sum(status_counts.values())

    # ---------- Summary cards ----------
    cards = ctk.CTkFrame(scroll, fg_color="transparent")
    cards.pack(anchor="w", pady=(0, 10))

    card_data = [
        ("Total", total, "#1a2433"),
        ("Pending", status_counts["Pending"], "#b54708"),
        ("In Progress", status_counts["In Progress"], "#0f6aa6"),
        ("Resolved", status_counts["Resolved"], "#157f3b"),
        ("Overdue", len(overdue), "#b42318"),
    ]

    for label, value, color in card_data:
        card = ctk.CTkFrame(cards, width=130, height=80,
                            fg_color="white", corner_radius=10)
        card.pack(side="left", padx=(0, 10))
        card.pack_propagate(False)

        ctk.CTkLabel(
            card, text=str(value),
            font=("Segoe UI", 26, "bold"), text_color=color
        ).pack(pady=(10, 0))

        ctk.CTkLabel(
            card, text=label,
            font=("Segoe UI", 12), text_color="#6b7789"
        ).pack()

    # ---------- Complaints per department ----------
    ctk.CTkLabel(
        scroll, text="Complaints per department",
        font=("Segoe UI", 16, "bold"), text_color="#1a2433"
    ).pack(anchor="w", pady=(10, 6))

    dept_table = ctk.CTkFrame(scroll, fg_color="white", corner_radius=10)
    dept_table.pack(anchor="w", fill="x", padx=(0, 10))

    widths = [140, 70, 80, 90, 80]
    headers = ["Department", "Total", "Pending", "In Progress", "Resolved"]

    for col, (text, width) in enumerate(zip(headers, widths)):
        ctk.CTkLabel(
            dept_table, text=text, width=width, anchor="w",
            font=("Segoe UI", 12, "bold"), text_color="#6b7789"
        ).grid(row=0, column=col, padx=8, pady=(8, 6))

    for r, row in enumerate(get_department_counts(), start=1):
        for col, (value, width) in enumerate(zip(row, widths)):
            ctk.CTkLabel(
                dept_table, text=str(value), width=width, anchor="w",
                font=("Segoe UI", 13,
                      "bold" if col == 1 else "normal"),
                text_color="#1a2433"
            ).grid(row=r, column=col, padx=8, pady=4)

        # Small bar showing this department's share of all complaints
        bar = ctk.CTkProgressBar(dept_table, width=150, height=10)
        bar.set(row[1] / total if total else 0)
        bar.grid(row=r, column=5, padx=8, pady=4)

    # ---------- Overdue complaints ----------
    ctk.CTkLabel(
        scroll,
        text=f"Overdue complaints (not resolved after {OVERDUE_DAYS} days)",
        font=("Segoe UI", 16, "bold"), text_color="#b42318"
    ).pack(anchor="w", pady=(18, 6))

    if not overdue:
        ctk.CTkLabel(
            scroll, text="No overdue complaints. Good work!",
            font=("Segoe UI", 13), text_color="#157f3b"
        ).pack(anchor="w", pady=(0, 10))
        return

    over_table = ctk.CTkFrame(scroll, fg_color="white", corner_radius=10)
    over_table.pack(anchor="w", fill="x", padx=(0, 10))

    o_widths = [35, 110, 95, 150, 85, 70]
    o_headers = ["ID", "Patient", "Department", "Subject",
                 "Status", "Days open"]

    for col, (text, width) in enumerate(zip(o_headers, o_widths)):
        ctk.CTkLabel(
            over_table, text=text, width=width, anchor="w",
            font=("Segoe UI", 12, "bold"), text_color="#6b7789"
        ).grid(row=0, column=col, padx=6, pady=(8, 6))

    for r, (cid, name, dept, subject, status, date, days) in enumerate(
            overdue, start=1):
        values = [str(cid), name[:14], dept, subject[:20], status,
                  str(days)]

        for col, (text, width) in enumerate(zip(values, o_widths)):
            ctk.CTkLabel(
                over_table, text=text, width=width, anchor="w",
                font=("Segoe UI", 12,
                      "bold" if col == 5 else "normal"),
                text_color="#b42318" if col == 5 else "#1a2433"
            ).grid(row=r, column=col, padx=6, pady=4)

        ctk.CTkButton(
            over_table, text="View", width=55, height=26,
            command=lambda c=cid: app.show_admin_details(user, c)
        ).grid(row=r, column=6, padx=6, pady=4)