import tkinter as tk
from tkinter import ttk, messagebox
import re
from gui import theme
from database.db_connection import DatabaseConnection
from mysql.connector import Error

class ParticipantsScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=theme.BG)
        self.db = DatabaseConnection()
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, minsize=380)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_form_frame()
        self.create_tree_frame()
        
        self.load_data()

    def create_form_frame(self):
        self.form_frame = tk.Frame(self, bg=theme.PANEL, padx=20, pady=18,
                       highlightthickness=1, highlightbackground=theme.BORDER)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        for column in range(4):
            self.form_frame.grid_columnconfigure(column, weight=1, uniform="participant_field")
        
        theme.section_title(self.form_frame, "Participant Details").grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 15))
        
        # Variables
        self.var_id = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_phone = tk.StringVar()
        self.var_dept = tk.StringVar()
        self.var_year = tk.StringVar()
        
        theme.field_label(self.form_frame, "Name:").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(4, 3), padx=(0, 8))
        theme.field_label(self.form_frame, "Email:").grid(
            row=1, column=2, columnspan=2, sticky="w", pady=(4, 3))
        self.entry_name = theme.styled_entry(self.form_frame, textvariable=self.var_name, width=25)
        self.entry_name.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 9), padx=(0, 8))
        
        self.entry_email = theme.styled_entry(self.form_frame, textvariable=self.var_email, width=25)
        self.entry_email.grid(row=2, column=2, columnspan=2, sticky="ew", pady=(0, 9))
        
        theme.field_label(self.form_frame, "Phone:").grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(2, 3), padx=(0, 8))
        theme.field_label(self.form_frame, "Department:").grid(
            row=3, column=2, columnspan=2, sticky="w", pady=(2, 3))
        self.entry_phone = theme.styled_entry(self.form_frame, textvariable=self.var_phone, width=25)
        self.entry_phone.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 9), padx=(0, 8))
        
        self.entry_dept = theme.styled_entry(self.form_frame, textvariable=self.var_dept, width=25)
        self.entry_dept.grid(row=4, column=2, columnspan=2, sticky="ew", pady=(0, 9))
        
        theme.field_label(self.form_frame, "Year of Study:").grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(2, 3))
        self.entry_year = theme.styled_entry(self.form_frame, textvariable=self.var_year, width=25)
        self.entry_year.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        
        theme.form_section(self.form_frame, "Actions").grid(
            row=7, column=0, columnspan=4, sticky="ew", pady=(2, 8))
        btn_frame = tk.Frame(self.form_frame, bg=theme.PANEL)
        btn_frame.grid(row=8, column=0, columnspan=4, pady=(0, 2))
        for column in range(3):
            btn_frame.grid_columnconfigure(column, weight=1, uniform="participant_actions")
        
        theme.make_button(btn_frame, "Add", self.add_participant, kind="primary").grid(row=0, column=0, sticky="ew", padx=4)
        theme.make_button(btn_frame, "Update", self.update_participant, kind="secondary").grid(row=0, column=1, sticky="ew", padx=4)
        theme.make_button(btn_frame, "Delete", self.delete_participant, kind="danger").grid(row=0, column=2, sticky="ew", padx=4)
        theme.make_button(btn_frame, "Clear", self.clear_form, kind="neutral").grid(row=1, column=0, columnspan=3, pady=(8, 0), sticky="ew", padx=5)

    def create_tree_frame(self):
        self.tree_frame = tk.Frame(self, bg=theme.BG)
        self.tree_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        self.tree_frame.grid_rowconfigure(1, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        
        self.var_search = tk.StringVar()
        search_frame = theme.search_bar(
            self.tree_frame, self.var_search, self.search_data, self.load_data,
            label="Search by Name:")
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        columns = ("ID", "Name", "Email", "Phone", "Department", "Year")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Department", text="Department")
        self.tree.heading("Year", text="Year")
        
        self.tree.column("ID", width=44, minwidth=40, stretch=False, anchor="center")
        self.tree.column("Name", width=110, minwidth=100, stretch=True)
        self.tree.column("Email", width=140, minwidth=125, stretch=True)
        self.tree.column("Phone", width=86, minwidth=78, stretch=True)
        self.tree.column("Department", width=130, minwidth=118, stretch=True)
        self.tree.column("Year", width=55, minwidth=50, stretch=False, anchor="center")
        
        y_scroll = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=y_scroll.set)
        
        self.tree.grid(row=1, column=0, sticky="nsew")
        y_scroll.grid(row=1, column=1, sticky="ns")
        self.tree.bind("<ButtonRelease-1>", self.get_cursor)

    def fetch_query(self, query, params=None):
        conn = self.db.get_connection()
        if not conn: return
            
        cursor = None
        try:
            self.tree.delete(*self.tree.get_children())
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            for row in cursor.fetchall():
                theme.insert_table_row(self.tree, row)
        except Error as e:
            messagebox.showerror("Database Error", f"Error fetching data:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def load_data(self):
        query = "SELECT participant_id, participant_name, email, phone, department, year_of_study FROM Participant ORDER BY participant_name"
        self.fetch_query(query)

    def search_data(self):
        search_term = self.var_search.get().strip()
        if not search_term:
            self.load_data()
            return
            
        query = "SELECT participant_id, participant_name, email, phone, department, year_of_study FROM Participant WHERE participant_name LIKE %s ORDER BY participant_name"
        self.fetch_query(query, (f"%{search_term}%",))

    def get_cursor(self, ev):
        cursor_row = self.tree.focus()
        if not cursor_row: return
            
        content = self.tree.item(cursor_row)
        row = content['values']
        
        self.var_id.set(row[0])
        self.var_name.set(row[1])
        self.var_email.set(row[2])
        self.var_phone.set(str(row[3]) if str(row[3]) != 'None' else "")
        self.var_dept.set(str(row[4]) if str(row[4]) != 'None' else "")
        self.var_year.set(str(row[5]) if str(row[5]) != 'None' else "")

    def clear_form(self):
        self.var_id.set("")
        self.var_name.set("")
        self.var_email.set("")
        self.var_phone.set("")
        self.var_dept.set("")
        self.var_year.set("")

    def validate_inputs(self):
        name = self.var_name.get().strip()
        email = self.var_email.get().strip()
        phone = self.var_phone.get().strip()
        dept = self.var_dept.get().strip()
        year_str = self.var_year.get().strip()
        
        if not all([name, email, dept, year_str]):
            messagebox.showerror("Error", "Name, Email, Department, and Year of Study are required.")
            return None
            
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, email):
            messagebox.showerror("Error", "Invalid email format.")
            return None
            
        try:
            year = int(year_str)
            if year <= 0:
                messagebox.showerror("Error", "Year of study must be a positive integer.")
                return None
        except ValueError:
            messagebox.showerror("Error", "Year of study must be a number.")
            return None
            
        return {
            'name': name,
            'email': email,
            'phone': phone or None,
            'dept': dept,
            'year': year
        }

    def add_participant(self):
        data = self.validate_inputs()
        if not data: return
            
        conn = self.db.get_connection()
        if not conn: return
            
        cursor = None
        try:
            cursor = conn.cursor()
            query = "INSERT INTO Participant (participant_name, email, phone, department, year_of_study) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (data['name'], data['email'], data['phone'], data['dept'], data['year']))
            conn.commit()
            messagebox.showinfo("Success", "Participant added successfully!")
            self.clear_form()
            self.load_data()
        except Error as e:
            if e.errno == 1062:  # ER_DUP_ENTRY
                messagebox.showerror("Duplicate Entry", "This email address is already registered.")
            else:
                messagebox.showerror("Database Error", f"Error adding participant:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def update_participant(self):
        pid = self.var_id.get()
        if not pid:
            messagebox.showerror("Error", "Please select a participant to update.")
            return
            
        data = self.validate_inputs()
        if not data: return
            
        conn = self.db.get_connection()
        if not conn: return
            
        cursor = None
        try:
            cursor = conn.cursor()
            query = "UPDATE Participant SET participant_name=%s, email=%s, phone=%s, department=%s, year_of_study=%s WHERE participant_id=%s"
            cursor.execute(query, (data['name'], data['email'], data['phone'], data['dept'], data['year'], pid))
            conn.commit()
            messagebox.showinfo("Success", "Participant updated successfully!")
            self.clear_form()
            self.load_data()
        except Error as e:
            if e.errno == 1062:
                messagebox.showerror("Duplicate Entry", "This email address is already registered to another participant.")
            else:
                messagebox.showerror("Database Error", f"Error updating participant:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def delete_participant(self):
        pid = self.var_id.get()
        if not pid:
            messagebox.showerror("Error", "Please select a participant to delete.")
            return
            
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this participant?")
        if not confirm: return
            
        conn = self.db.get_connection()
        if not conn: return
            
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Participant WHERE participant_id=%s", (pid,))
            conn.commit()
            messagebox.showinfo("Success", "Participant deleted successfully!")
            self.clear_form()
            self.load_data()
        except Error as e:
            if e.errno == 1451:
                messagebox.showerror("Constraint Error", "Cannot delete this participant because they have associated registrations, waitlist entries, payments, or attendance records.")
            else:
                messagebox.showerror("Database Error", f"Error deleting participant:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
