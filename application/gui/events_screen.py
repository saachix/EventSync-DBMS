import tkinter as tk
from tkinter import ttk, messagebox
from gui import theme
from database.db_connection import DatabaseConnection
from mysql.connector import Error
import datetime

class EventsScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=theme.BG)
        self.db = DatabaseConnection()

        # Split into left (form) and right (treeview)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, minsize=380)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_form_frame()
        self.create_tree_frame()
        
        self.load_categories_and_coordinators()
        self.load_data()

    def create_form_frame(self):
        self.form_frame = tk.Frame(self, bg=theme.PANEL, padx=20, pady=12,
                       highlightthickness=1, highlightbackground=theme.BORDER)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        for column in range(4):
            self.form_frame.grid_columnconfigure(column, weight=1, uniform="event_field")
        
        theme.section_title(self.form_frame, "Event Details").grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))
        
        # Variables
        self.var_id = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_category = tk.StringVar()
        self.var_coordinator = tk.StringVar()
        self.var_date = tk.StringVar()
        self.var_capacity = tk.StringVar()
        self.var_fee = tk.StringVar()
        self.var_status = tk.StringVar(value="Open")
        
        # Dictionaries to map names to IDs
        self.category_map = {}
        self.coordinator_map = {}
        
        # Form Fields
        theme.field_label(self.form_frame, "Event Name:").grid(
            row=1, column=0, columnspan=4, sticky="w", pady=(2, 2))
        self.entry_name = theme.styled_entry(self.form_frame, textvariable=self.var_name, width=25)
        self.entry_name.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, 5))
        
        theme.field_label(self.form_frame, "Category:").grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(1, 2), padx=(0, 8))
        theme.field_label(self.form_frame, "Coordinator:").grid(
            row=3, column=2, columnspan=2, sticky="w", pady=(1, 2))
        self.combo_category = ttk.Combobox(self.form_frame, textvariable=self.var_category, width=22, state="readonly")
        self.combo_category.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 5), padx=(0, 8))
        
        self.combo_coordinator = ttk.Combobox(self.form_frame, textvariable=self.var_coordinator, width=22, state="readonly")
        self.combo_coordinator.grid(row=4, column=2, columnspan=2, sticky="ew", pady=(0, 5))
        
        theme.field_label(self.form_frame, "Date (YYYY-MM-DD):").grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(1, 2), padx=(0, 8))
        theme.field_label(self.form_frame, "Status:").grid(
            row=5, column=2, columnspan=2, sticky="w", pady=(1, 2))
        self.entry_date = theme.styled_entry(self.form_frame, textvariable=self.var_date, width=25)
        self.entry_date.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 5), padx=(0, 8))
        
        self.combo_status = ttk.Combobox(self.form_frame, textvariable=self.var_status, values=["Open", "Closed", "Cancelled"], width=22, state="readonly")
        self.combo_status.grid(row=6, column=2, columnspan=2, sticky="ew", pady=(0, 5))
        
        theme.field_label(self.form_frame, "Max Capacity:").grid(
            row=7, column=0, columnspan=2, sticky="w", pady=(1, 2), padx=(0, 8))
        theme.field_label(self.form_frame, "Registration Fee:").grid(
            row=7, column=2, columnspan=2, sticky="w", pady=(1, 2))
        self.entry_capacity = theme.styled_entry(self.form_frame, textvariable=self.var_capacity, width=25)
        self.entry_capacity.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(0, 5), padx=(0, 8))
        self.entry_fee = theme.styled_entry(self.form_frame, textvariable=self.var_fee, width=25)
        self.entry_fee.grid(row=8, column=2, columnspan=2, sticky="ew", pady=(0, 5))

        theme.field_label(self.form_frame, "Description:").grid(
            row=9, column=0, columnspan=4, sticky="w", pady=(1, 2))
        self.text_desc = tk.Text(self.form_frame, width=25, height=4, font=theme.FONT_BODY,
                     bg=theme.PANEL_ALT, fg=theme.TEXT, relief="flat",
                     highlightthickness=1, highlightbackground=theme.BORDER,
                     highlightcolor=theme.ACCENT, wrap="word")
        self.text_desc.grid(row=10, column=0, columnspan=4, sticky="ew", pady=(0, 6))
        
        # Buttons
        theme.form_section(self.form_frame, "Actions").grid(
            row=11, column=0, columnspan=4, sticky="ew", pady=(1, 4))
        btn_frame = tk.Frame(self.form_frame, bg=theme.PANEL)
        btn_frame.grid(row=12, column=0, columnspan=4, pady=(0, 0))
        for column in range(3):
            btn_frame.grid_columnconfigure(column, weight=1, uniform="event_actions")
        
        theme.make_button(btn_frame, "Add", self.add_event, kind="primary").grid(row=0, column=0, sticky="ew", padx=4)
        theme.make_button(btn_frame, "Update", self.update_event, kind="secondary").grid(row=0, column=1, sticky="ew", padx=4)
        theme.make_button(btn_frame, "Delete", self.delete_event, kind="danger").grid(row=0, column=2, sticky="ew", padx=4)
        theme.make_button(btn_frame, "Clear", self.clear_form, kind="neutral").grid(row=1, column=0, columnspan=3, pady=(5, 0), sticky="ew", padx=5)

    def create_tree_frame(self):
        self.tree_frame = tk.Frame(self, bg=theme.BG)
        self.tree_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        self.tree_frame.grid_rowconfigure(1, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        
        # Search Top Bar
        self.var_search = tk.StringVar()
        search_frame = theme.search_bar(
            self.tree_frame, self.var_search, self.search_data, self.load_data,
            label="Search by Name:")
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Treeview
        columns = ("ID", "Name", "Category", "Coordinator", "Date", "Capacity", "Fee", "Status", "Desc")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Coordinator", text="Coord.")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Capacity", text="Cap.")
        self.tree.heading("Fee", text="Fee")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Desc", text="Desc")
        
        self.tree.column("ID", width=36, minwidth=34, stretch=False, anchor="center")
        self.tree.column("Name", width=90, minwidth=80, stretch=True)
        self.tree.column("Category", width=62, minwidth=55, stretch=True)
        self.tree.column("Coordinator", width=70, minwidth=60, stretch=True)
        self.tree.column("Date", width=68, minwidth=64, stretch=False, anchor="center")
        self.tree.column("Capacity", width=50, minwidth=46, stretch=False, anchor="center")
        self.tree.column("Fee", width=72, minwidth=68, stretch=False, anchor="e")
        self.tree.column("Status", width=60, minwidth=56, stretch=False, anchor="center")
        self.tree.column("Desc", width=40, minwidth=32, stretch=True)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        self.tree.grid(row=1, column=0, sticky="nsew")
        y_scroll.grid(row=1, column=1, sticky="ns")
        x_scroll.grid(row=2, column=0, sticky="ew")
        
        self.tree.bind("<ButtonRelease-1>", self.get_cursor)

    def load_categories_and_coordinators(self):
        conn = self.db.get_connection()
        if not conn:
            return
            
        cursor = None
        try:
            cursor = conn.cursor()
            
            # Categories
            cursor.execute("SELECT category_id, category_name FROM Category")
            for cid, cname in cursor.fetchall():
                self.category_map[cname] = cid
            self.combo_category['values'] = list(self.category_map.keys())
            
            # Coordinators
            cursor.execute("SELECT coordinator_id, coordinator_name FROM Coordinator")
            for cid, cname in cursor.fetchall():
                self.coordinator_map[cname] = cid
            self.combo_coordinator['values'] = list(self.coordinator_map.keys())
            
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load references:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def fetch_events_query(self, query, params=None):
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
            messagebox.showerror("Database Error", f"Error fetching data:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def load_data(self):
        query = """
        SELECT e.event_id, e.event_name, c.category_name, co.coordinator_name, 
               e.event_date, e.max_capacity, e.registration_fee, e.status, e.description
        FROM Event e
        JOIN Category c ON e.category_id = c.category_id
        JOIN Coordinator co ON e.coordinator_id = co.coordinator_id
        ORDER BY e.event_date DESC
        """
        self.fetch_events_query(query)

    def search_data(self):
        search_term = self.var_search.get().strip()
        if not search_term:
            self.load_data()
            return
            
        query = """
        SELECT e.event_id, e.event_name, c.category_name, co.coordinator_name, 
               e.event_date, e.max_capacity, e.registration_fee, e.status, e.description
        FROM Event e
        JOIN Category c ON e.category_id = c.category_id
        JOIN Coordinator co ON e.coordinator_id = co.coordinator_id
        WHERE e.event_name LIKE %s
        ORDER BY e.event_date DESC
        """
        self.fetch_events_query(query, (f"%{search_term}%",))

    def get_cursor(self, ev):
        cursor_row = self.tree.focus()
        if not cursor_row:
            return
            
        content = self.tree.item(cursor_row)
        row = content['values']
        
        self.var_id.set(row[0])
        self.var_name.set(row[1])
        self.var_category.set(row[2])
        self.var_coordinator.set(row[3])
        self.var_date.set(row[4])
        self.var_capacity.set(row[5])
        self.var_fee.set(row[6])
        self.var_status.set(row[7])
        
        self.text_desc.delete("1.0", tk.END)
        if str(row[8]) != "None":
            self.text_desc.insert(tk.END, str(row[8]))

    def clear_form(self):
        self.var_id.set("")
        self.var_name.set("")
        self.var_category.set("")
        self.var_coordinator.set("")
        self.var_date.set("")
        self.var_capacity.set("")
        self.var_fee.set("")
        self.var_status.set("Open")
        self.text_desc.delete("1.0", tk.END)

    def validate_inputs(self):
        name = self.var_name.get().strip()
        cat = self.var_category.get()
        coord = self.var_coordinator.get()
        date_str = self.var_date.get().strip()
        cap_str = self.var_capacity.get().strip()
        fee_str = self.var_fee.get().strip()
        
        if not all([name, cat, coord, date_str, cap_str, fee_str]):
            messagebox.showerror("Error", "All fields except Description are required!")
            return None
            
        # Validate Date
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid Date format. Use YYYY-MM-DD")
            return None
            
        # Validate Capacity
        try:
            cap = int(cap_str)
            if cap <= 0:
                messagebox.showerror("Error", "Maximum capacity must be a positive integer.")
                return None
        except ValueError:
            messagebox.showerror("Error", "Capacity must be an integer.")
            return None
            
        # Validate Fee
        try:
            fee = float(fee_str)
            if fee < 0:
                messagebox.showerror("Error", "Registration fee cannot be negative.")
                return None
        except ValueError:
            messagebox.showerror("Error", "Registration fee must be a number.")
            return None
            
        return {
            'name': name,
            'cat_id': self.category_map[cat],
            'coord_id': self.coordinator_map[coord],
            'date': date_str,
            'cap': cap,
            'fee': fee,
            'status': self.var_status.get(),
            'desc': self.text_desc.get("1.0", tk.END).strip()
        }

    def add_event(self):
        data = self.validate_inputs()
        if not data:
            return
            
        conn = self.db.get_connection()
        if not conn:
            return
            
        cursor = None
        try:
            cursor = conn.cursor()
            query = """INSERT INTO Event 
                       (event_name, category_id, coordinator_id, event_date, description, max_capacity, registration_fee, status)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (data['name'], data['cat_id'], data['coord_id'], data['date'], 
                                   data['desc'], data['cap'], data['fee'], data['status']))
            conn.commit()
            messagebox.showinfo("Success", "Event added successfully!")
            self.clear_form()
            self.load_data()
        except Error as e:
            messagebox.showerror("Database Error", f"Error adding event:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def update_event(self):
        event_id = self.var_id.get()
        if not event_id:
            messagebox.showerror("Error", "Please select an event to update.")
            return
            
        data = self.validate_inputs()
        if not data:
            return
            
        conn = self.db.get_connection()
        if not conn:
            return
            
        cursor = None
        try:
            cursor = conn.cursor()
            query = """UPDATE Event SET 
                       event_name=%s, category_id=%s, coordinator_id=%s, event_date=%s, 
                       description=%s, max_capacity=%s, registration_fee=%s, status=%s
                       WHERE event_id=%s"""
            cursor.execute(query, (data['name'], data['cat_id'], data['coord_id'], data['date'], 
                                   data['desc'], data['cap'], data['fee'], data['status'], event_id))
            conn.commit()
            messagebox.showinfo("Success", "Event updated successfully!")
            self.clear_form()
            self.load_data()
        except Error as e:
            messagebox.showerror("Database Error", f"Error updating event:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def delete_event(self):
        event_id = self.var_id.get()
        if not event_id:
            messagebox.showerror("Error", "Please select an event to delete.")
            return
            
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this event?")
        if not confirm:
            return
            
        conn = self.db.get_connection()
        if not conn:
            return
            
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Event WHERE event_id=%s", (event_id,))
            conn.commit()
            messagebox.showinfo("Success", "Event deleted successfully!")
            self.clear_form()
            self.load_data()
        except Error as e:
            if e.errno == 1451:
                messagebox.showerror("Constraint Error", "Cannot delete this event because it has associated sessions or registrations.")
            else:
                messagebox.showerror("Database Error", f"Error deleting event:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
