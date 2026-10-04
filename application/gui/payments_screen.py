import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from gui import theme
from database.db_connection import DatabaseConnection
from mysql.connector import Error


class PaymentsScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=theme.BG)
        self.db = DatabaseConnection()

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, minsize=380)
        self.grid_rowconfigure(0, weight=1)

        # {display_label: registration_id}
        self.reg_map = {}
        # payment_id of the row currently loaded in the form
        self.selected_payment_id = None

        self.create_form_frame()
        self.create_right_frame()

        self.load_registration_dropdown()
        self.load_data()
        self.refresh_summary()

    # ------------------------------------------------------------------
    # LEFT PANEL — form
    # ------------------------------------------------------------------
    def create_form_frame(self):
        self.form_frame = tk.Frame(self, bg=theme.PANEL, padx=20, pady=18,
                                   highlightthickness=1, highlightbackground=theme.BORDER)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        for column in range(4):
            self.form_frame.grid_columnconfigure(column, weight=1, uniform="payment_field")

        theme.section_title(self.form_frame, "Payment Details").grid(
            row=0, column=0, columnspan=4, pady=(0, 15), sticky="w")

        # Variables
        self.var_registration = tk.StringVar()
        self.var_amount       = tk.StringVar()
        self.var_date         = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        self.var_method       = tk.StringVar(value="UPI")
        self.var_status       = tk.StringVar(value="Paid")

        # Registration combobox
        theme.field_label(self.form_frame, "Registration:").grid(
            row=1, column=0, columnspan=4, sticky="w", pady=(3, 3))
        self.combo_reg = ttk.Combobox(
            self.form_frame, textvariable=self.var_registration, width=30, state="readonly")
        self.combo_reg.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, 9))

        theme.field_label(self.form_frame, "Amount:").grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(2, 3), padx=(0, 8))
        theme.field_label(self.form_frame, "Payment Method:").grid(
            row=3, column=2, columnspan=2, sticky="w", pady=(2, 3))
        theme.styled_entry(self.form_frame, textvariable=self.var_amount, width=18).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(0, 9), padx=(0, 8))

        ttk.Combobox(
            self.form_frame, textvariable=self.var_method,
            values=["UPI", "Card", "Cash", "Net Banking", "Free"],
            width=18, state="readonly"
        ).grid(row=4, column=2, columnspan=2, sticky="ew", pady=(0, 9))

        theme.field_label(self.form_frame, "Payment Date:").grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(2, 3), padx=(0, 8))
        theme.field_label(self.form_frame, "Payment Status:").grid(
            row=5, column=2, columnspan=2, sticky="w", pady=(2, 3))
        theme.styled_entry(self.form_frame, textvariable=self.var_date, width=18).grid(
            row=6, column=0, columnspan=2, sticky="ew", pady=(0, 10), padx=(0, 8))
        ttk.Combobox(
            self.form_frame, textvariable=self.var_status,
            values=["Paid", "Pending", "Failed", "Refunded"],
            width=18, state="readonly"
        ).grid(row=6, column=2, columnspan=2, sticky="ew", pady=(0, 10))

        # Buttons
        theme.form_section(self.form_frame, "Actions").grid(
            row=8, column=0, columnspan=4, sticky="ew", pady=(2, 8))
        btn_frame = tk.Frame(self.form_frame, bg=theme.PANEL)
        btn_frame.grid(row=9, column=0, columnspan=4, pady=(0, 2))
        for column in range(2):
            btn_frame.grid_columnconfigure(column, weight=1, uniform="payment_actions")

        theme.make_button(btn_frame, "Add Payment", self.add_payment, kind="primary").grid(row=0, column=0, sticky="ew", padx=4)
        theme.make_button(btn_frame, "Update", self.update_payment, kind="secondary").grid(row=0, column=1, sticky="ew", padx=4)
        theme.make_button(btn_frame, "Delete", self.delete_payment, kind="danger").grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        theme.make_button(btn_frame, "Clear Form", self.clear_form, kind="neutral").grid(row=1, column=1, sticky="ew", padx=4, pady=4)

        # Summary panel
        summary_frame = tk.LabelFrame(
            self.form_frame, text="Payment Summary", bg=theme.PANEL_ALT,
            fg=theme.BRAND, font=theme.FONT_BODY_B, bd=1, relief="solid",
            padx=12, pady=10)
        summary_frame.grid(row=7, column=0, columnspan=4, sticky="ew", pady=(8, 14))

        self.lbl_total_payments = tk.Label(
            summary_frame, text="Total Payments: -", bg=theme.PANEL_ALT,
            fg=theme.TEXT, font=theme.FONT_BODY)
        self.lbl_total_payments.pack(anchor="w")

        self.lbl_total_revenue = tk.Label(
            summary_frame, text="Total Revenue: -", bg=theme.PANEL_ALT,
            fg=theme.BRAND, font=theme.FONT_BODY_B)
        self.lbl_total_revenue.pack(anchor="w")

    # ------------------------------------------------------------------
    # RIGHT PANEL — treeview + search
    # ------------------------------------------------------------------
    def create_right_frame(self):
        right_frame = tk.Frame(self, bg=theme.BG)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Search bar
        self.var_search = tk.StringVar()
        search_frame = theme.search_bar(
            right_frame, self.var_search, self.search_data, self.load_data,
            label="Search (Event or Participant):", entry_width=25)
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        # Treeview
        columns = ("Pay ID", "Reg ID", "Event", "Participant",
                   "Amount", "Date", "Method", "Status")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings")

        col_widths = {"Pay ID": 42, "Reg ID": 42, "Event": 96,
                  "Participant": 105, "Amount": 90,
                  "Date": 76, "Method": 80, "Status": 68}
        for col in columns:
            self.tree.heading(col, text=col)
            fixed = col in ("Pay ID", "Reg ID", "Amount", "Date", "Method", "Status")
            self.tree.column(col, width=col_widths.get(col, 90),
                             minwidth=max(38, col_widths.get(col, 90) - 15),
                             stretch=not fixed,
                             anchor="center" if fixed else "w")

        y_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL,   command=self.tree.yview)
        x_scroll = ttk.Scrollbar(right_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.grid(row=1, column=0, sticky="nsew")
        y_scroll.grid(row=1, column=1, sticky="ns")
        x_scroll.grid(row=2, column=0, sticky="ew")
        self.tree.bind("<ButtonRelease-1>", self.on_row_select)

    # ------------------------------------------------------------------
    # Data loading helpers
    # ------------------------------------------------------------------
    def load_registration_dropdown(self):
        """Populate the Registration combobox with readable labels."""
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
                label = f"Reg #{reg_id} — {pname} — {ename}"
                self.reg_map[label] = reg_id
            self.combo_reg['values'] = list(self.reg_map.keys())
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load registrations:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    def _fetch_into_tree(self, query, params=None):
        """Execute query and populate the payments Treeview."""
        conn = self.db.get_connection()
        if not conn:
            return
        cursor = None
        try:
            self.tree.delete(*self.tree.get_children())
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            for row in cursor.fetchall():
                theme.insert_table_row(self.tree, row)
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading payments:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    def load_data(self):
        self.var_search.set("")
        self._fetch_into_tree("""
            SELECT p.payment_id, p.registration_id,
                   e.event_name, pt.participant_name,
                   p.amount, p.payment_date,
                   p.payment_method, p.payment_status
            FROM Payment p
            JOIN Registration r  ON p.registration_id = r.registration_id
            JOIN Event e         ON r.event_id         = e.event_id
            JOIN Participant pt  ON r.participant_id    = pt.participant_id
            ORDER BY p.payment_id DESC
        """)

    def search_data(self):
        term = self.var_search.get().strip()
        if not term:
            self.load_data()
            return
        s = f"%{term}%"
        self._fetch_into_tree("""
            SELECT p.payment_id, p.registration_id,
                   e.event_name, pt.participant_name,
                   p.amount, p.payment_date,
                   p.payment_method, p.payment_status
            FROM Payment p
            JOIN Registration r  ON p.registration_id = r.registration_id
            JOIN Event e         ON r.event_id         = e.event_id
            JOIN Participant pt  ON r.participant_id    = pt.participant_id
            WHERE e.event_name LIKE %s OR pt.participant_name LIKE %s
            ORDER BY p.payment_id DESC
        """, (s, s))

    def refresh_summary(self):
        """Pull totals directly from MySQL — no hard-coded values."""
        conn = self.db.get_connection()
        if not conn:
            return
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*), IFNULL(SUM(amount), 0)
                FROM Payment
            """)
            count, total = cursor.fetchone()
            self.lbl_total_payments.config(text=f"Total Payments: {count}")
            self.lbl_total_revenue.config(text=f"Total Revenue: Rs.{float(total):,.2f}")
        except Error as e:
            messagebox.showerror("Database Error", f"Error refreshing summary:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    # ------------------------------------------------------------------
    # Form helpers
    # ------------------------------------------------------------------
    def on_row_select(self, _event=None):
        row_id = self.tree.focus()
        if not row_id:
            return
        values = self.tree.item(row_id)['values']
        # values: (Pay ID, Reg ID, Event, Participant, Amount, Date, Method, Status)
        self.selected_payment_id = values[0]

        # Locate matching registration label
        reg_id = values[1]
        matching_label = next(
            (lbl for lbl, rid in self.reg_map.items() if rid == reg_id), "")
        self.var_registration.set(matching_label)
        self.var_amount.set(str(values[4]))
        self.var_date.set(str(values[5]))
        self.var_method.set(values[6])
        self.var_status.set(values[7])

    def clear_form(self):
        self.selected_payment_id = None
        self.var_registration.set("")
        self.var_amount.set("")
        self.var_date.set(datetime.datetime.now().strftime("%Y-%m-%d"))
        self.var_method.set("UPI")
        self.var_status.set("Paid")

    def _validate_inputs(self):
        """Return (reg_id, amount, date_str, method, status) or raise ValueError."""
        reg_label = self.var_registration.get()
        if not reg_label or reg_label not in self.reg_map:
            raise ValueError("Please select a Registration.")

        amount_str = self.var_amount.get().strip()
        if not amount_str:
            raise ValueError("Amount is required.")
        try:
            amount = float(amount_str)
        except ValueError:
            raise ValueError("Amount must be a valid number.")
        if amount < 0:
            raise ValueError("Amount cannot be negative.")

        date_str = self.var_date.get().strip()
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date. Use YYYY-MM-DD format.")

        method = self.var_method.get().strip()
        if not method:
            raise ValueError("Payment method is required.")

        status = self.var_status.get().strip()
        if not status:
            raise ValueError("Payment status is required.")

        return self.reg_map[reg_label], amount, date_str, method, status

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------
    def add_payment(self):
        try:
            reg_id, amount, date_str, method, status = self._validate_inputs()
        except ValueError as ve:
            messagebox.showerror("Validation Error", str(ve))
            return

        conn = self.db.get_connection()
        if not conn:
            return
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Payment (registration_id, amount, payment_date,
                                     payment_method, payment_status)
                VALUES (%s, %s, %s, %s, %s)
            """, (reg_id, amount, date_str, method, status))
            conn.commit()
            messagebox.showinfo("Success", "Payment recorded successfully!")
            self.clear_form()
            self.load_data()
            self.refresh_summary()
        except Error as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Error recording payment:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    def update_payment(self):
        if not self.selected_payment_id:
            messagebox.showerror("Error", "Please select a payment from the list to update.")
            return

        try:
            _reg_id, amount, date_str, method, status = self._validate_inputs()
        except ValueError as ve:
            messagebox.showerror("Validation Error", str(ve))
            return

        conn = self.db.get_connection()
        if not conn:
            return
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Payment
                SET amount=%s, payment_date=%s, payment_method=%s, payment_status=%s
                WHERE payment_id=%s
            """, (amount, date_str, method, status, self.selected_payment_id))
            conn.commit()
            messagebox.showinfo("Success", "Payment updated successfully!")
            self.clear_form()
            self.load_data()
            self.refresh_summary()
        except Error as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Error updating payment:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()

    def delete_payment(self):
        if not self.selected_payment_id:
            messagebox.showerror("Error", "Please select a payment from the list to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete payment ID {self.selected_payment_id}? This cannot be undone.")
        if not confirm:
            return

        conn = self.db.get_connection()
        if not conn:
            return
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Payment WHERE payment_id=%s",
                           (self.selected_payment_id,))
            conn.commit()
            messagebox.showinfo("Success", "Payment deleted successfully.")
            self.clear_form()
            self.load_data()
            self.refresh_summary()
        except Error as e:
            conn.rollback()
            if e.errno == 1451:
                messagebox.showerror(
                    "Constraint Error",
                    "Cannot delete this payment because it has related records.")
            else:
                messagebox.showerror("Database Error", f"Error deleting payment:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn:   conn.close()
