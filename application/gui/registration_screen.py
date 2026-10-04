import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from gui import theme
from database.db_connection import DatabaseConnection
from mysql.connector import Error

class RegistrationScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=theme.BG)
        self.db = DatabaseConnection()
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, minsize=380)
        self.grid_rowconfigure(0, weight=1)
        
        self.event_map = {}
        self.participant_map = {}
        
        self.create_form_frame()
        self.create_tree_frames()
        
        self.load_dropdowns()
        self.load_data()

    def create_form_frame(self):
        self.form_frame = tk.Frame(self, bg=theme.PANEL, padx=20, pady=18,
                       highlightthickness=1, highlightbackground=theme.BORDER)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.form_frame.grid_columnconfigure(1, weight=1)
        
        theme.section_title(self.form_frame, "Registration Desk").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        theme.form_section(self.form_frame, "Registration Details").grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        
        # Variables
        self.var_reg_id = tk.StringVar()
        self.var_wait_id = tk.StringVar()
        self.var_event = tk.StringVar()
        self.var_participant = tk.StringVar()
        self.var_date = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        self.var_status = tk.StringVar(value="Confirmed")
        
        labels = ["Event:", "Participant:", "Date (YYYY-MM-DD):", "Status:"]
        for i, text in enumerate(labels):
            theme.field_label(self.form_frame, text).grid(
                row=i+2, column=0, sticky="w", pady=5, padx=(0, 10))
            
        self.combo_event = ttk.Combobox(self.form_frame, textvariable=self.var_event, width=25, state="readonly")
        self.combo_event.grid(row=2, column=1, sticky="ew", pady=5)
        self.combo_event.bind("<<ComboboxSelected>>", self.update_capacity_display)
        
        self.combo_participant = ttk.Combobox(self.form_frame, textvariable=self.var_participant, width=25, state="readonly")
        self.combo_participant.grid(row=3, column=1, sticky="ew", pady=5)
        
        self.entry_date = theme.styled_entry(self.form_frame, textvariable=self.var_date, width=28)
        self.entry_date.grid(row=4, column=1, sticky="ew", pady=5)
        
        self.combo_status = ttk.Combobox(self.form_frame, textvariable=self.var_status, values=["Confirmed", "Pending", "Cancelled"], width=25, state="readonly")
        self.combo_status.grid(row=5, column=1, sticky="ew", pady=5)
        
        # Capacity Info Box
        self.cap_frame = tk.LabelFrame(self.form_frame, text="Event Capacity Info",
                           bg=theme.PANEL_ALT, fg=theme.BRAND,
                           font=theme.FONT_BODY_B, bd=1,
                           relief="solid", padx=12, pady=10)
        self.cap_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(12, 10))
        
        self.lbl_cap_max = tk.Label(self.cap_frame, text="Maximum Capacity: -", bg=theme.PANEL_ALT, fg=theme.TEXT, font=theme.FONT_BODY)
        self.lbl_cap_max.pack(anchor="w")
        self.lbl_cap_reg = tk.Label(self.cap_frame, text="Registered: -", bg=theme.PANEL_ALT, fg=theme.TEXT, font=theme.FONT_BODY)
        self.lbl_cap_reg.pack(anchor="w")
        self.lbl_cap_rem = tk.Label(self.cap_frame, text="Seats Remaining: -", bg=theme.PANEL_ALT, fg=theme.BRAND, font=theme.FONT_BODY_B)
        self.lbl_cap_rem.pack(anchor="w")
        
        # Buttons
        theme.form_section(self.form_frame, "Actions").grid(
            row=7, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        btn_frame = tk.Frame(self.form_frame, bg=theme.PANEL)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=(0, 2))
        
        theme.make_button(btn_frame, "Register", self.register_participant, kind="primary").grid(row=0, column=0, padx=5, pady=5)
        theme.make_button(btn_frame, "Clear Form", self.clear_form, kind="neutral").grid(row=0, column=1, padx=5, pady=5)
        
        theme.make_button(btn_frame, "Delete Registration", self.delete_registration, kind="danger").grid(row=1, column=0, padx=5, pady=5)
        theme.make_button(btn_frame, "Delete Waitlist", self.delete_waitlist, kind="danger").grid(row=1, column=1, padx=5, pady=5)

    def create_tree_frames(self):
        self.right_frame = tk.Frame(self, bg=theme.BG)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        self.right_frame.grid_rowconfigure(1, weight=3) # Reg Tree
        self.right_frame.grid_rowconfigure(3, weight=2) # Waitlist Tree
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        # Search Bar
        self.var_search = tk.StringVar()
        search_frame = theme.search_bar(
            self.right_frame, self.var_search, self.search_data, self.load_data,
            label="Search (Event or Participant):", entry_width=25)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Registrations Tree
        theme.panel_title(self.right_frame, "Registrations").grid(row=1, column=0, sticky="nw")
        
        reg_tree_frame = tk.Frame(self.right_frame)
        reg_tree_frame.grid(row=1, column=0, sticky="nsew", pady=(25, 10))
        
        reg_cols = ("ID", "Event", "Participant", "Date", "Status")
        self.reg_tree = ttk.Treeview(reg_tree_frame, columns=reg_cols, show="headings")
        for col in reg_cols:
            self.reg_tree.heading(col, text=col)
        self.reg_tree.column("ID", width=48, minwidth=42, stretch=False, anchor="center")
        self.reg_tree.column("Event", width=170, minwidth=120, stretch=True)
        self.reg_tree.column("Participant", width=170, minwidth=120, stretch=True)
        self.reg_tree.column("Date", width=105, minwidth=90, stretch=False, anchor="center")
        self.reg_tree.column("Status", width=105, minwidth=85, stretch=False, anchor="center")
        
        reg_scroll = ttk.Scrollbar(reg_tree_frame, orient=tk.VERTICAL, command=self.reg_tree.yview)
        self.reg_tree.configure(yscrollcommand=reg_scroll.set)
        self.reg_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        reg_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.reg_tree.bind("<ButtonRelease-1>", self.get_reg_cursor)
        
        # Waitlist Tree
        theme.panel_title(self.right_frame, "Waitlist").grid(row=3, column=0, sticky="nw")
        
        wait_tree_frame = tk.Frame(self.right_frame)
        wait_tree_frame.grid(row=3, column=0, sticky="nsew", pady=(25, 0))
        
        wait_cols = ("Wait ID", "Event", "Participant", "Date", "Position", "Status")
        self.wait_tree = ttk.Treeview(wait_tree_frame, columns=wait_cols, show="headings")
        for col in wait_cols:
            self.wait_tree.heading(col, text=col)
        self.wait_tree.column("Wait ID", width=65, minwidth=55, stretch=False, anchor="center")
        self.wait_tree.column("Event", width=165, minwidth=115, stretch=True)
        self.wait_tree.column("Participant", width=165, minwidth=115, stretch=True)
        self.wait_tree.column("Date", width=105, minwidth=90, stretch=False, anchor="center")
        self.wait_tree.column("Position", width=75, minwidth=60, stretch=False, anchor="center")
        self.wait_tree.column("Status", width=105, minwidth=85, stretch=False, anchor="center")
        
        wait_scroll = ttk.Scrollbar(wait_tree_frame, orient=tk.VERTICAL, command=self.wait_tree.yview)
        wait_x_scroll = ttk.Scrollbar(wait_tree_frame, orient=tk.HORIZONTAL, command=self.wait_tree.xview)
        self.wait_tree.configure(yscrollcommand=wait_scroll.set, xscrollcommand=wait_x_scroll.set)
        self.wait_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        wait_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        wait_x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.wait_tree.bind("<ButtonRelease-1>", self.get_wait_cursor)

    def load_dropdowns(self):
        conn = self.db.get_connection()
        if not conn: return
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT event_id, event_name FROM Event ORDER BY event_date DESC")
            for eid, ename in cursor.fetchall():
                self.event_map[ename] = eid
            self.combo_event['values'] = list(self.event_map.keys())
            
            cursor.execute("SELECT participant_id, participant_name FROM Participant ORDER BY participant_name")
            for pid, pname in cursor.fetchall():
                self.participant_map[pname] = pid
            self.combo_participant['values'] = list(self.participant_map.keys())
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load dropdowns:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_event_capacity_info(self, event_id):
        conn = self.db.get_connection()
        if not conn: return 0, 0
        cursor = None
        try:
            cursor = conn.cursor()
            query = """
                SELECT e.max_capacity, COUNT(r.registration_id)
                FROM Event e
                LEFT JOIN Registration r ON e.event_id = r.event_id
                WHERE e.event_id = %s
                GROUP BY e.event_id, e.max_capacity
            """
            cursor.execute(query, (event_id,))
            result = cursor.fetchone()
            if result:
                return result[0], result[1]
            return 0, 0
        except Error as e:
            messagebox.showerror("Database Error", f"Error checking capacity:\n{e}")
            return 0, 0
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def update_capacity_display(self, event=None):
        ename = self.var_event.get()
        if ename in self.event_map:
            eid = self.event_map[ename]
            max_cap, reg_count = self.get_event_capacity_info(eid)
            rem = max_cap - reg_count
            
            self.lbl_cap_max.config(text=f"Maximum Capacity: {max_cap}")
            self.lbl_cap_reg.config(text=f"Registered: {reg_count}")
            self.lbl_cap_rem.config(text=f"Seats Remaining: {rem}")
            
            if rem <= 0:
                self.lbl_cap_rem.config(fg=theme.DANGER)
            else:
                self.lbl_cap_rem.config(fg=theme.SUCCESS)
        else:
            self.lbl_cap_max.config(text="Maximum Capacity: -")
            self.lbl_cap_reg.config(text="Registered: -")
            self.lbl_cap_rem.config(text="Seats Remaining: -")

    def fetch_trees(self, reg_query, wait_query, params=None):
        conn = self.db.get_connection()
        if not conn: return
        cursor = None
        try:
            self.reg_tree.delete(*self.reg_tree.get_children())
            self.wait_tree.delete(*self.wait_tree.get_children())
            
            cursor = conn.cursor()
            
            # Registrations
            cursor.execute(reg_query, params or ())
            for row in cursor.fetchall():
                theme.insert_table_row(self.reg_tree, row)
                
            # Waitlist
            cursor.execute(wait_query, params or ())
            for row in cursor.fetchall():
                theme.insert_table_row(self.wait_tree, row)
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error fetching data:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def load_data(self):
        reg_q = """
            SELECT r.registration_id, e.event_name, p.participant_name, r.registration_date, r.registration_status
            FROM Registration r
            JOIN Event e ON r.event_id = e.event_id
            JOIN Participant p ON r.participant_id = p.participant_id
            ORDER BY r.registration_date DESC
        """
        wait_q = """
            SELECT w.waitlist_id, e.event_name, p.participant_name, w.waitlist_date, w.position, w.status
            FROM Waitlist w
            JOIN Event e ON w.event_id = e.event_id
            JOIN Participant p ON w.participant_id = p.participant_id
            ORDER BY w.event_id, w.position ASC
        """
        self.fetch_trees(reg_q, wait_q)

    def search_data(self):
        term = self.var_search.get().strip()
        if not term:
            self.load_data()
            return
            
        search_str = f"%{term}%"
        
        reg_q = """
            SELECT r.registration_id, e.event_name, p.participant_name, r.registration_date, r.registration_status
            FROM Registration r
            JOIN Event e ON r.event_id = e.event_id
            JOIN Participant p ON r.participant_id = p.participant_id
            WHERE e.event_name LIKE %s OR p.participant_name LIKE %s
            ORDER BY r.registration_date DESC
        """
        wait_q = """
            SELECT w.waitlist_id, e.event_name, p.participant_name, w.waitlist_date, w.position, w.status
            FROM Waitlist w
            JOIN Event e ON w.event_id = e.event_id
            JOIN Participant p ON w.participant_id = p.participant_id
            WHERE e.event_name LIKE %s OR p.participant_name LIKE %s
            ORDER BY w.event_id, w.position ASC
        """
        self.fetch_trees(reg_q, wait_q, (search_str, search_str))

    def clear_form(self):
        self.var_reg_id.set("")
        self.var_wait_id.set("")
        self.var_event.set("")
        self.var_participant.set("")
        self.var_date.set(datetime.datetime.now().strftime("%Y-%m-%d"))
        self.var_status.set("Confirmed")
        self.update_capacity_display()

    def get_reg_cursor(self, ev):
        row_id = self.reg_tree.focus()
        if not row_id: return
        row = self.reg_tree.item(row_id)['values']
        
        self.var_reg_id.set(row[0])
        self.var_wait_id.set("") # Clear wait id
        self.var_event.set(row[1])
        self.var_participant.set(row[2])
        self.var_date.set(row[3])
        self.var_status.set(row[4])
        self.update_capacity_display()

    def get_wait_cursor(self, ev):
        row_id = self.wait_tree.focus()
        if not row_id: return
        row = self.wait_tree.item(row_id)['values']
        
        self.var_wait_id.set(row[0])
        self.var_reg_id.set("") # Clear reg id
        self.var_event.set(row[1])
        self.var_participant.set(row[2])
        self.var_date.set(row[3])
        self.var_status.set(row[5])
        self.update_capacity_display()

    def register_participant(self):
        ename = self.var_event.get()
        pname = self.var_participant.get()
        rdate = self.var_date.get().strip()
        rstatus = self.var_status.get()
        
        if not all([ename, pname, rdate]):
            messagebox.showerror("Error", "Event, Participant, and Date are required fields.")
            return
            
        try:
            datetime.datetime.strptime(rdate, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid Date format. Use YYYY-MM-DD")
            return
            
        eid = self.event_map[ename]
        pid = self.participant_map[pname]
        
        conn = self.db.get_connection()
        if not conn: return
        cursor = None
        try:
            cursor = conn.cursor()
            
            # Step 2: Check existing registration
            cursor.execute("SELECT 1 FROM Registration WHERE event_id=%s AND participant_id=%s", (eid, pid))
            if cursor.fetchone():
                messagebox.showinfo("Already Registered", "Participant is already registered for this event.")
                return
                
            # Check if waitlisted
            cursor.execute("SELECT 1 FROM Waitlist WHERE event_id=%s AND participant_id=%s", (eid, pid))
            is_waitlisted = cursor.fetchone()
            
            # Step 3: Check capacity
            max_cap, reg_count = self.get_event_capacity_info(eid)
            
            if reg_count < max_cap:
                # Insert Registration
                try:
                    cursor.execute("""INSERT INTO Registration (event_id, participant_id, registration_date, registration_status) 
                                      VALUES (%s, %s, %s, %s)""", (eid, pid, rdate, rstatus))
                    conn.commit()
                    messagebox.showinfo("Success", "Participant registered successfully!")
                except Error as tx_err:
                    conn.rollback()
                    raise tx_err
            else:
                # Event is full, offer Waitlist
                if is_waitlisted:
                    messagebox.showinfo("Already Waitlisted", "Event is full and participant is already on the waitlist.")
                    return
                    
                offer = messagebox.askyesno("Event Full", "The selected event has reached its maximum capacity.\n\nWould you like to add the participant to the Waitlist instead?")
                if offer:
                    self.add_to_waitlist(conn, cursor, eid, pid, rdate)
                    
            self.clear_form()
            self.load_data()
            self.update_capacity_display()
            
        except Error as e:
            messagebox.showerror("Database Error", f"Error during registration:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def add_to_waitlist(self, conn, cursor, eid, pid, wdate):
        try:
            # Get next position
            cursor.execute("SELECT IFNULL(MAX(position), 0) + 1 FROM Waitlist WHERE event_id=%s", (eid,))
            next_pos = cursor.fetchone()[0]
            
            cursor.execute("""INSERT INTO Waitlist (event_id, participant_id, waitlist_date, position, status) 
                              VALUES (%s, %s, %s, %s, 'Waiting')""", (eid, pid, wdate, next_pos))
            conn.commit()
            messagebox.showinfo("Waitlist Success", f"Participant added to waitlist at Position {next_pos}.")
        except Error as tx_err:
            conn.rollback()
            if tx_err.errno == 1062:
                messagebox.showerror("Waitlist Duplicate", "Participant is already on the waitlist for this event.")
            else:
                raise tx_err

    def delete_registration(self):
        rid = self.var_reg_id.get()
        if not rid:
            messagebox.showerror("Error", "Please select a Registration to delete.")
            return
            
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this registration?")
        if not confirm: return
            
        conn = self.db.get_connection()
        if not conn: return
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Registration WHERE registration_id=%s", (rid,))
            conn.commit()
            messagebox.showinfo("Success", "Registration deleted successfully.")
            self.clear_form()
            self.load_data()
            self.update_capacity_display()
        except Error as e:
            if e.errno == 1451:
                messagebox.showerror("Constraint Error", "Cannot delete this registration because it has related attendance, payment, certificate, or feedback records.")
            else:
                messagebox.showerror("Database Error", f"Error deleting registration:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def delete_waitlist(self):
        wid = self.var_wait_id.get()
        if not wid:
            messagebox.showerror("Error", "Please select a Waitlist entry to delete.")
            return
            
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to remove this participant from the waitlist?")
        if not confirm: return
            
        conn = self.db.get_connection()
        if not conn: return
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Waitlist WHERE waitlist_id=%s", (wid,))
            conn.commit()
            messagebox.showinfo("Success", "Waitlist entry deleted successfully.")
            self.clear_form()
            self.load_data()
            self.update_capacity_display()
        except Error as e:
            messagebox.showerror("Database Error", f"Error deleting waitlist entry:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
