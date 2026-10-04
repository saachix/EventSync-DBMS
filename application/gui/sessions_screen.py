import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from gui import theme
from database.db_connection import DatabaseConnection
from mysql.connector import Error

class SessionsScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=theme.BG)
        self.db = DatabaseConnection()
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, minsize=380)
        self.grid_rowconfigure(0, weight=1)
        
        self.event_map = {}
        self.venue_map = {}
        self.venue_cap_map = {}
        
        self.create_form_frame()
        self.create_tree_frame()
        
        self.load_dropdowns()
        self.load_data()

    def create_form_frame(self):
        self.form_frame = tk.Frame(self, bg=theme.PANEL, padx=20, pady=18,
                       highlightthickness=1, highlightbackground=theme.BORDER)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        for column in range(4):
            self.form_frame.grid_columnconfigure(column, weight=1, uniform="session_field")
        
        theme.section_title(self.form_frame, "Session Details").grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 15))
        
        # Variables
        self.var_id = tk.StringVar()
        self.var_title = tk.StringVar()
        self.var_event = tk.StringVar()
        self.var_venue = tk.StringVar()
        self.var_date = tk.StringVar()
        self.var_start = tk.StringVar()
        self.var_end = tk.StringVar()
        self.var_attendance = tk.StringVar()
        
        theme.field_label(self.form_frame, "Session Title:").grid(
            row=1, column=0, columnspan=4, sticky="w", pady=(4, 3))
        self.entry_title = theme.styled_entry(self.form_frame, textvariable=self.var_title, width=25)
        self.entry_title.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, 8))
        
        theme.field_label(self.form_frame, "Event:").grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(2, 3), padx=(0, 8))
        theme.field_label(self.form_frame, "Venue:").grid(
            row=3, column=2, columnspan=2, sticky="w", pady=(2, 3))
        self.combo_event = ttk.Combobox(self.form_frame, textvariable=self.var_event, width=22, state="readonly")
        self.combo_event.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 8), padx=(0, 8))
        
        self.combo_venue = ttk.Combobox(self.form_frame, textvariable=self.var_venue, width=22, state="readonly")
        self.combo_venue.grid(row=4, column=2, columnspan=2, sticky="ew", pady=(0, 8))
        self.combo_venue.bind("<<ComboboxSelected>>", self.update_venue_capacity_label)
        
        self.lbl_capacity = tk.Label(self.form_frame, text="Capacity: -", fg=theme.TEXT_MUTED, bg=theme.PANEL, font=theme.FONT_BODY_B)
        self.lbl_capacity.grid(row=5, column=2, columnspan=2, sticky="w", pady=(0, 8))
        
        theme.field_label(self.form_frame, "Date (YYYY-MM-DD):").grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(2, 3), padx=(0, 8))
        self.entry_date = theme.styled_entry(self.form_frame, textvariable=self.var_date, width=25)
        self.entry_date.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 8), padx=(0, 8))
        
        theme.field_label(self.form_frame, "Start Time:").grid(
            row=7, column=0, columnspan=2, sticky="w", pady=(2, 3), padx=(0, 8))
        theme.field_label(self.form_frame, "End Time:").grid(
            row=7, column=2, columnspan=2, sticky="w", pady=(2, 3))
        self.entry_start = theme.styled_entry(self.form_frame, textvariable=self.var_start, width=25)
        self.entry_start.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(0, 8), padx=(0, 8))
        
        self.entry_end = theme.styled_entry(self.form_frame, textvariable=self.var_end, width=25)
        self.entry_end.grid(row=8, column=2, columnspan=2, sticky="ew", pady=(0, 8))
        
        theme.field_label(self.form_frame, "Expected Attendance:").grid(
            row=9, column=0, columnspan=2, sticky="w", pady=(2, 3))
        self.entry_att = theme.styled_entry(self.form_frame, textvariable=self.var_attendance, width=25)
        self.entry_att.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        
        theme.form_section(self.form_frame, "Actions").grid(
            row=11, column=0, columnspan=4, sticky="ew", pady=(2, 8))
        btn_frame = tk.Frame(self.form_frame, bg=theme.PANEL)
        btn_frame.grid(row=12, column=0, columnspan=4, pady=(0, 2))
        for column in range(3):
            btn_frame.grid_columnconfigure(column, weight=1, uniform="session_actions")
        
        theme.make_button(btn_frame, "Add", self.add_session, kind="primary").grid(row=0, column=0, sticky="ew", padx=4)
        theme.make_button(btn_frame, "Update", self.update_session, kind="secondary").grid(row=0, column=1, sticky="ew", padx=4)
        theme.make_button(btn_frame, "Delete", self.delete_session, kind="danger").grid(row=0, column=2, sticky="ew", padx=4)
        theme.make_button(btn_frame, "Clear", self.clear_form, kind="neutral").grid(row=1, column=0, columnspan=3, pady=(8, 0), sticky="ew", padx=5)

    def update_venue_capacity_label(self, event=None):
        venue_name = self.var_venue.get()
        if venue_name in self.venue_map:
            vid = self.venue_map[venue_name]
            cap = self.venue_cap_map.get(vid, "-")
            self.lbl_capacity.config(text=f"Capacity: {cap}")
        else:
            self.lbl_capacity.config(text="Capacity: -")

    def create_tree_frame(self):
        self.tree_frame = tk.Frame(self, bg=theme.BG)
        self.tree_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        
        columns = ("ID", "Title", "Event", "Venue", "Date", "Start Time", "End Time", "Attendance")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Event", text="Event")
        self.tree.heading("Venue", text="Venue")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Start Time", text="Start")
        self.tree.heading("End Time", text="End")
        self.tree.heading("Attendance", text="Expected")
        
        self.tree.column("ID", width=38, minwidth=36, stretch=False, anchor="center")
        self.tree.column("Title", width=86, minwidth=82, stretch=True)
        self.tree.column("Event", width=79, minwidth=74, stretch=True)
        self.tree.column("Venue", width=80, minwidth=72, stretch=True)
        self.tree.column("Date", width=74, minwidth=70, stretch=False, anchor="center")
        self.tree.column("Start Time", width=58, minwidth=54, stretch=False, anchor="center")
        self.tree.column("End Time", width=58, minwidth=54, stretch=False, anchor="center")
        self.tree.column("Attendance", width=74, minwidth=70, stretch=False, anchor="center")
        
        y_scroll = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        
        self.tree.bind("<ButtonRelease-1>", self.get_cursor)

    def load_dropdowns(self):
        conn = self.db.get_connection()
        if not conn: return
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT event_id, event_name FROM Event")
            for eid, ename in cursor.fetchall():
                self.event_map[ename] = eid
            self.combo_event['values'] = list(self.event_map.keys())
            
            cursor.execute("SELECT venue_id, venue_name, capacity FROM Venue")
            for vid, vname, cap in cursor.fetchall():
                self.venue_map[vname] = vid
                self.venue_cap_map[vid] = cap
            self.combo_venue['values'] = list(self.venue_map.keys())
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load references:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def load_data(self):
        conn = self.db.get_connection()
        if not conn: return
        cursor = None
        try:
            self.tree.delete(*self.tree.get_children())
            cursor = conn.cursor()
            query = """
                SELECT s.session_id, s.session_title, e.event_name, v.venue_name,
                       s.session_date, s.start_time, s.end_time, s.expected_attendance
                FROM Session s
                JOIN Event e ON s.event_id = e.event_id
                JOIN Venue v ON s.venue_id = v.venue_id
                ORDER BY s.session_date DESC, s.start_time
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                theme.insert_table_row(self.tree, row)
        except Error as e:
            messagebox.showerror("Database Error", f"Error fetching data:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_cursor(self, ev):
        cursor_row = self.tree.focus()
        if not cursor_row: return
            
        content = self.tree.item(cursor_row)
        row = content['values']
        
        self.var_id.set(row[0])
        self.var_title.set(row[1])
        self.var_event.set(row[2])
        self.var_venue.set(row[3])
        self.var_date.set(row[4])
        self.var_start.set(str(row[5]))
        self.var_end.set(str(row[6]))
        self.var_attendance.set(row[7])
        
        self.update_venue_capacity_label()

    def clear_form(self):
        self.var_id.set("")
        self.var_title.set("")
        self.var_event.set("")
        self.var_venue.set("")
        self.var_date.set("")
        self.var_start.set("")
        self.var_end.set("")
        self.var_attendance.set("")
        self.lbl_capacity.config(text="Capacity: -")

    def parse_time(self, time_str):
        try:
            if len(time_str.split(":")) == 3:
                return datetime.datetime.strptime(time_str, "%H:%M:%S").time()
            return datetime.datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            return None

    def validate_and_check_overlap(self, session_id=None):
        title = self.var_title.get().strip()
        event = self.var_event.get()
        venue = self.var_venue.get()
        date_str = self.var_date.get().strip()
        start_str = self.var_start.get().strip()
        end_str = self.var_end.get().strip()
        att_str = self.var_attendance.get().strip()
        
        if not all([title, event, venue, date_str, start_str, end_str, att_str]):
            messagebox.showerror("Error", "All fields are required.")
            return None
            
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid Date format. Use YYYY-MM-DD")
            return None
            
        start_time = self.parse_time(start_str)
        end_time = self.parse_time(end_str)
        if not start_time or not end_time:
            messagebox.showerror("Error", "Invalid Time format. Use HH:MM or HH:MM:SS")
            return None
            
        if end_time <= start_time:
            messagebox.showerror("Error", "End time must be after start time.")
            return None
            
        try:
            att = int(att_str)
            if att < 0:
                messagebox.showerror("Error", "Attendance must be a positive integer.")
                return None
        except ValueError:
            messagebox.showerror("Error", "Expected attendance must be a number.")
            return None
            
        vid = self.venue_map[venue]
        capacity = self.venue_cap_map[vid]
        if att > capacity:
            messagebox.showerror("Error", f"Expected attendance ({att}) exceeds the selected venue's capacity ({capacity}).")
            return None
            
        # Check Overlap
        conn = self.db.get_connection()
        if not conn: return None
        cursor = None
        try:
            cursor = conn.cursor()
            query = """
                SELECT session_id FROM Session 
                WHERE venue_id = %s AND session_date = %s 
                AND start_time < %s AND end_time > %s
            """
            params = [vid, date_str, end_time.strftime("%H:%M:%S"), start_time.strftime("%H:%M:%S")]
            
            if session_id:
                query += " AND session_id != %s"
                params.append(session_id)
                
            cursor.execute(query, tuple(params))
            conflict = cursor.fetchone()
            if conflict:
                messagebox.showerror("Error", "The venue is already occupied during that time. Please choose a different time or venue.")
                return None
        except Error as e:
            messagebox.showerror("Database Error", f"Error checking overlaps:\n{e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
            
        return {
            'title': title,
            'event_id': self.event_map[event],
            'venue_id': vid,
            'date': date_str,
            'start': start_time.strftime("%H:%M:%S"),
            'end': end_time.strftime("%H:%M:%S"),
            'att': att
        }

    def add_session(self):
        data = self.validate_and_check_overlap()
        if not data: return
            
        conn = self.db.get_connection()
        if not conn: return
        cursor = None
        try:
            cursor = conn.cursor()
            query = """INSERT INTO Session (event_id, venue_id, session_title, session_date, start_time, end_time, expected_attendance) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (data['event_id'], data['venue_id'], data['title'], data['date'], data['start'], data['end'], data['att']))
            conn.commit()
            messagebox.showinfo("Success", "Session added successfully!")
            self.clear_form()
            self.load_data()
        except Error as e:
            messagebox.showerror("Database Error", f"Error adding session:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def update_session(self):
        sid = self.var_id.get()
        if not sid:
            messagebox.showerror("Error", "Please select a session to update.")
            return
            
        data = self.validate_and_check_overlap(sid)
        if not data: return
            
        conn = self.db.get_connection()
        if not conn: return
        cursor = None
        try:
            cursor = conn.cursor()
            query = """UPDATE Session SET event_id=%s, venue_id=%s, session_title=%s, session_date=%s, start_time=%s, end_time=%s, expected_attendance=%s 
                       WHERE session_id=%s"""
            cursor.execute(query, (data['event_id'], data['venue_id'], data['title'], data['date'], data['start'], data['end'], data['att'], sid))
            conn.commit()
            messagebox.showinfo("Success", "Session updated successfully!")
            self.clear_form()
            self.load_data()
        except Error as e:
            messagebox.showerror("Database Error", f"Error updating session:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def delete_session(self):
        sid = self.var_id.get()
        if not sid:
            messagebox.showerror("Error", "Please select a session to delete.")
            return
            
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this session?")
        if not confirm: return
            
        conn = self.db.get_connection()
        if not conn: return
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Session WHERE session_id=%s", (sid,))
            conn.commit()
            messagebox.showinfo("Success", "Session deleted successfully!")
            self.clear_form()
            self.load_data()
        except Error as e:
            if e.errno == 1451:
                messagebox.showerror("Constraint Error", "Cannot delete this session because it has associated attendance or speaker records.")
            else:
                messagebox.showerror("Database Error", f"Error deleting session:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
