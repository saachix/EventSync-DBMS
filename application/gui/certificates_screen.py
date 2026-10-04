import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from gui import theme
from database.db_connection import DatabaseConnection
from mysql.connector import Error

ELIGIBLE_THRESHOLD = 75.0   # project-defined rule: >= 75% to be eligible


class CertificatesScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=theme.BG)
        self.db = DatabaseConnection()

        self.grid_columnconfigure(0, weight=0, minsize=380)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # {display_label: registration_id}
        self.reg_map = {}
        # currently selected registration_id (int or None)
        self.current_reg_id = None

        self.create_left_panel()
        self.create_right_panel()

        self.load_registrations()
        self.load_certificates()

    # ------------------------------------------------------------------ #
    #  LEFT PANEL — eligibility checker + generate button
    # ------------------------------------------------------------------ #
    def create_left_panel(self):
        left = tk.Frame(self, bg=theme.PANEL, padx=20, pady=18,
                highlightthickness=1, highlightbackground=theme.BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left.grid_columnconfigure(1, weight=1)

        theme.section_title(left, "Certificate Eligibility").grid(
            row=0, column=0, columnspan=2, pady=(0, 15), sticky="w")

        # Registration selector
        theme.field_label(left, "Registration:").grid(
            row=1, column=0, sticky="w", pady=6, padx=(0, 8))
        self.var_reg = tk.StringVar()
        self.combo_reg = ttk.Combobox(left, textvariable=self.var_reg,
                                       state="readonly", width=32)
        self.combo_reg.grid(row=1, column=1, sticky="ew", pady=6)
        self.combo_reg.bind("<<ComboboxSelected>>", self.on_reg_selected)

        # Info box
        info_frame = tk.LabelFrame(
            left, text="Attendance Summary", bg=theme.PANEL_ALT, fg=theme.BRAND,
            font=theme.FONT_BODY_B, bd=1, relief="solid", padx=14, pady=12)
        info_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        self.lbl_participant  = tk.Label(info_frame, text="Participant: -",
                                          bg=theme.PANEL_ALT, fg=theme.TEXT, anchor="w")
        self.lbl_event        = tk.Label(info_frame, text="Event: -",
                                          bg=theme.PANEL_ALT, fg=theme.TEXT, anchor="w")
        self.lbl_total_sess   = tk.Label(info_frame, text="Total Sessions: -",
                                          bg=theme.PANEL_ALT, fg=theme.TEXT, anchor="w")
        self.lbl_attended     = tk.Label(info_frame, text="Sessions Attended: -",
                                          bg=theme.PANEL_ALT, fg=theme.TEXT, anchor="w")
        self.lbl_pct          = tk.Label(info_frame, text="Attendance: -",
                                          bg=theme.PANEL_ALT, fg=theme.BRAND, font=theme.FONT_BODY_B,
                                          anchor="w")
        self.lbl_eligibility  = tk.Label(info_frame, text="Eligibility: -",
                                          bg=theme.PANEL_ALT, fg=theme.BRAND, font=theme.FONT_BODY_B,
                                          anchor="w")
        self.lbl_cert_status  = tk.Label(info_frame, text="Certificate Status: -",
                                          bg=theme.PANEL_ALT, fg=theme.TEXT, anchor="w")

        for lbl in (self.lbl_participant, self.lbl_event, self.lbl_total_sess,
                    self.lbl_attended, self.lbl_pct, self.lbl_eligibility,
                    self.lbl_cert_status):
            lbl.pack(fill="x", pady=3)
            lbl.configure(wraplength=330)
        self.lbl_pct.configure(font=theme.FONT_H1)
        self.lbl_eligibility.configure(font=theme.FONT_H1)
        self.lbl_cert_status.configure(font=theme.FONT_BODY_B)

        # Action buttons
        theme.form_section(left, "Certificate Actions").grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(14, 8))
        btn_frame = tk.Frame(left, bg=theme.PANEL)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(0, 2))
        btn_frame.grid_columnconfigure(0, weight=1, uniform="certificate_actions")
        btn_frame.grid_columnconfigure(1, weight=1, uniform="certificate_actions")

        theme.make_button(btn_frame, "Generate Certificate",
                  self.generate_certificate, kind="success").grid(row=0, column=0, sticky="ew", padx=4)

        theme.make_button(btn_frame, "Delete Certificate",
                  self.delete_certificate, kind="danger").grid(row=0, column=1, sticky="ew", padx=4)

        theme.make_button(btn_frame, "Clear",
                          self.clear_form, kind="neutral").grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=(7, 0))

    # ------------------------------------------------------------------ #
    #  RIGHT PANEL — certificate list + search
    # ------------------------------------------------------------------ #
    def create_right_panel(self):
        right = tk.Frame(self, bg=theme.BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # Search bar
        self.var_search = tk.StringVar()
        search_frame = theme.search_bar(
            right, self.var_search, self.search_certificates,
            self.load_certificates, label="Search (Participant or Event):",
            entry_width=25)
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew",
                          pady=(0, 8))

        # Treeview
        cols = ("Cert ID", "Reg ID", "Participant", "Event",
                "Date", "Type", "Status")
        self.tree = ttk.Treeview(right, columns=cols, show="headings")

        widths = {"Cert ID": 48, "Reg ID": 48, "Participant": 118,
              "Event": 120, "Date": 80, "Type": 86, "Status": 68}
        for col in cols:
            self.tree.heading(col, text=col)
            fixed = col in ("Cert ID", "Reg ID", "Date", "Type", "Status")
            self.tree.column(col, width=widths.get(col, 90),
                             minwidth=max(45, widths.get(col, 90) - 18),
                             stretch=not fixed,
                             anchor="center" if fixed else "w")

        y_scroll = ttk.Scrollbar(right, orient=tk.VERTICAL,
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=y_scroll.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        y_scroll.grid(row=1, column=1, sticky="ns")
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

    # ------------------------------------------------------------------ #
    #  Data loading
    # ------------------------------------------------------------------ #
    def load_registrations(self):
        conn = self.db.get_connection()
        if not conn:
            return
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.registration_id, p.participant_name, e.event_name
                FROM Registration r
                JOIN Participant p ON r.participant_id = p.participant_id
                JOIN Event e       ON r.event_id       = e.event_id
                ORDER BY r.registration_id
            """)
            self.reg_map.clear()
            for reg_id, pname, ename in cursor.fetchall():
                label = f"Reg #{reg_id} -- {pname} -- {ename}"
                self.reg_map[label] = reg_id
            self.combo_reg['values'] = list(self.reg_map.keys())
        except Error as e:
            messagebox.showerror("Database Error",
                                  f"Failed to load registrations:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    def _cert_query(self, extra_where="", params=()):
        base = """
            SELECT c.certificate_id, c.registration_id,
                   p.participant_name, e.event_name,
                   c.certificate_date, c.certificate_type,
                   c.certificate_status
            FROM Certificate c
            JOIN Registration r  ON c.registration_id = r.registration_id
            JOIN Participant p   ON r.participant_id   = p.participant_id
            JOIN Event e         ON r.event_id         = e.event_id
        """
        return base + extra_where + " ORDER BY c.certificate_id DESC", params

    def load_certificates(self):
        self.var_search.set("")
        self._populate_tree(*self._cert_query())

    def search_certificates(self):
        term = self.var_search.get().strip()
        if not term:
            self.load_certificates()
            return
        s = f"%{term}%"
        query, _ = self._cert_query(
            " WHERE p.participant_name LIKE %s OR e.event_name LIKE %s")
        self._populate_tree(query, (s, s))

    def _populate_tree(self, query, params=()):
        conn = self.db.get_connection()
        if not conn:
            return
        cursor = None
        try:
            self.tree.delete(*self.tree.get_children())
            cursor = conn.cursor()
            cursor.execute(query, params)
            for row in cursor.fetchall():
                theme.insert_table_row(self.tree, row)
        except Error as e:
            messagebox.showerror("Database Error",
                                  f"Error loading certificates:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    # ------------------------------------------------------------------ #
    #  Eligibility calculation — the core logic
    # ------------------------------------------------------------------ #
    def get_attendance_info(self, reg_id):
        """
        Returns (participant_name, event_name, total_sessions,
                 sessions_attended, pct, cert_row_or_None).
        Missing attendance records count as Not Attended per the spec.
        """
        conn = self.db.get_connection()
        if not conn:
            return None
        cursor = None
        try:
            cursor = conn.cursor()

            # Participant + event for this registration
            cursor.execute("""
                SELECT p.participant_name, e.event_name, r.event_id
                FROM Registration r
                JOIN Participant p ON r.participant_id = p.participant_id
                JOIN Event e       ON r.event_id       = e.event_id
                WHERE r.registration_id = %s
            """, (reg_id,))
            row = cursor.fetchone()
            if not row:
                return None
            pname, ename, event_id = row

            # Total sessions for that event
            cursor.execute(
                "SELECT COUNT(*) FROM Session WHERE event_id = %s", (event_id,))
            total_sessions = cursor.fetchone()[0]

            # Sessions where this registration is marked Present
            cursor.execute("""
                SELECT COUNT(*)
                FROM Attendance
                WHERE registration_id = %s AND attendance_status = 'Present'
            """, (reg_id,))
            attended = cursor.fetchone()[0]

            pct = (attended / total_sessions * 100) if total_sessions > 0 else 0.0

            # Existing certificate for this registration (if any)
            cursor.execute(
                "SELECT certificate_id, certificate_date, certificate_type, "
                "certificate_status FROM Certificate WHERE registration_id = %s",
                (reg_id,))
            cert_row = cursor.fetchone()

            return pname, ename, total_sessions, attended, pct, cert_row

        except Error as e:
            messagebox.showerror("Database Error",
                                  f"Error calculating attendance:\n{e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    # ------------------------------------------------------------------ #
    #  UI event handlers
    # ------------------------------------------------------------------ #
    def on_reg_selected(self, _event=None):
        label = self.var_reg.get()
        if not label or label not in self.reg_map:
            return
        self.current_reg_id = self.reg_map[label]
        self._refresh_info_panel(self.current_reg_id)

    def _refresh_info_panel(self, reg_id):
        info = self.get_attendance_info(reg_id)
        if info is None:
            return
        pname, ename, total, attended, pct, cert_row = info

        self.lbl_participant.config(text=f"Participant: {pname}")
        self.lbl_event.config(text=f"Event: {ename}")
        self.lbl_total_sess.config(text=f"Total Sessions: {total}")
        self.lbl_attended.config(text=f"Sessions Attended: {attended}")
        self.lbl_pct.config(text=f"Attendance: {pct:.1f}%")

        if pct >= ELIGIBLE_THRESHOLD:
            self.lbl_eligibility.config(text="Eligibility: ELIGIBLE",
                                         fg=theme.SUCCESS)
        else:
            self.lbl_eligibility.config(text="Eligibility: NOT ELIGIBLE",
                                         fg=theme.DANGER)

        if cert_row:
            cert_id, cert_date, cert_type, cert_status = cert_row
            self.lbl_cert_status.config(
                text=f"Certificate Status: {cert_status} "
                     f"(ID {cert_id}, {cert_date}, {cert_type})")
        else:
            self.lbl_cert_status.config(text="Certificate Status: Not Generated")

    def on_tree_select(self, _event=None):
        row_id = self.tree.focus()
        if not row_id:
            return
        values = self.tree.item(row_id)['values']
        reg_id = values[1]   # Reg ID column

        # Find and set the matching combobox label
        matching = next(
            (lbl for lbl, rid in self.reg_map.items() if rid == reg_id), "")
        if matching:
            self.var_reg.set(matching)
            self.current_reg_id = reg_id
            self._refresh_info_panel(reg_id)

    def clear_form(self):
        self.var_reg.set("")
        self.current_reg_id = None
        for lbl in (self.lbl_participant, self.lbl_event, self.lbl_total_sess,
                    self.lbl_attended, self.lbl_pct, self.lbl_eligibility,
                    self.lbl_cert_status):
            lbl.config(text=lbl.cget("text").split(":")[0] + ": -",
                   fg=theme.TEXT)

    # ------------------------------------------------------------------ #
    #  CRUD operations
    # ------------------------------------------------------------------ #
    def generate_certificate(self):
        if not self.current_reg_id:
            messagebox.showerror("Error",
                                  "Please select a registration first.")
            return

        info = self.get_attendance_info(self.current_reg_id)
        if info is None:
            return
        pname, ename, total, attended, pct, cert_row = info

        # Duplicate check (application-level, before hitting UNIQUE constraint)
        if cert_row:
            messagebox.showinfo(
                "Already Generated",
                "Certificate has already been generated for this registration.")
            return

        # Eligibility check
        if pct < ELIGIBLE_THRESHOLD:
            messagebox.showerror(
                "Not Eligible",
                f"Certificate not eligible.\n"
                f"Attendance: {pct:.1f}%\n"
                f"Minimum attendance required is {ELIGIBLE_THRESHOLD:.0f}%.")
            return

        # Insert certificate — use conventions from sample data
        cert_date = datetime.date.today().strftime("%Y-%m-%d")

        conn = self.db.get_connection()
        if not conn:
            return
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Certificate
                    (registration_id, certificate_date, certificate_type,
                     certificate_status)
                VALUES (%s, %s, %s, %s)
            """, (self.current_reg_id, cert_date, "Participation", "Issued"))
            conn.commit()
            messagebox.showinfo("Success",
                                 f"Certificate generated for {pname}!")
            self._refresh_info_panel(self.current_reg_id)
            self.load_certificates()
        except Error as e:
            conn.rollback()
            if e.errno == 1062:
                messagebox.showinfo(
                    "Already Generated",
                    "Certificate has already been generated for this registration.")
            else:
                messagebox.showerror("Database Error",
                                      f"Error generating certificate:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    def delete_certificate(self):
        if not self.current_reg_id:
            messagebox.showerror("Error",
                                  "Please select a registration first.")
            return

        info = self.get_attendance_info(self.current_reg_id)
        if info is None:
            return
        _pname, _ename, _total, _attended, _pct, cert_row = info

        if not cert_row:
            messagebox.showinfo("No Certificate",
                                 "No certificate exists for this registration.")
            return

        cert_id = cert_row[0]
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete Certificate ID {cert_id}? This cannot be undone.")
        if not confirm:
            return

        conn = self.db.get_connection()
        if not conn:
            return
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Certificate WHERE certificate_id = %s",
                           (cert_id,))
            conn.commit()
            messagebox.showinfo("Success", "Certificate deleted successfully.")
            self._refresh_info_panel(self.current_reg_id)
            self.load_certificates()
        except Error as e:
            conn.rollback()
            if e.errno == 1451:
                messagebox.showerror(
                    "Constraint Error",
                    "Cannot delete this certificate because it has related records.")
            else:
                messagebox.showerror("Database Error",
                                      f"Error deleting certificate:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()
