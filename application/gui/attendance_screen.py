import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from gui import theme
from database.db_connection import DatabaseConnection
from mysql.connector import Error

class AttendanceScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=theme.BG)
        self.db = DatabaseConnection()
        
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=6)
        self.grid_rowconfigure(0, weight=1)
        
        self.event_map = {}
        self.session_map = {}
        
        self.create_left_frame()
        self.create_right_frame()
        
        self.load_events()
        self.load_all_attendance()

    def create_left_frame(self):
        left_frame = tk.Frame(self, bg=theme.PANEL, padx=16, pady=16,
                      highlightthickness=1, highlightbackground=theme.BORDER)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_frame.grid_rowconfigure(3, weight=1)
        left_frame.grid_columnconfigure(1, weight=1)
        
        theme.section_title(left_frame, "Mark Attendance").grid(row=0, column=0, columnspan=2, pady=(0, 8), sticky="w")
        
        theme.field_label(left_frame, "Event:").grid(row=1, column=0, sticky="w", pady=5, padx=(0, 8))
        self.var_event = tk.StringVar()
        self.combo_event = ttk.Combobox(left_frame, textvariable=self.var_event, state="readonly")
        self.combo_event.grid(row=1, column=1, sticky="ew", pady=5)
        self.combo_event.bind("<<ComboboxSelected>>", self.on_event_selected)
        
        theme.field_label(left_frame, "Session:").grid(row=2, column=0, sticky="w", pady=5, padx=(0, 8))
        self.var_session = tk.StringVar()
        self.combo_session = ttk.Combobox(left_frame, textvariable=self.var_session, state="readonly")
        self.combo_session.grid(row=2, column=1, sticky="ew", pady=5)
        self.combo_session.bind("<<ComboboxSelected>>", self.on_session_selected)
        
        # Participants Treeview for the selected session
        cols = ("Reg ID", "Participant", "Status", "Check-in")
        self.roster_tree = ttk.Treeview(left_frame, columns=cols, show="headings")
        for col in cols:
            self.roster_tree.heading(col, text=col)
        self.roster_tree.column("Reg ID", width=45, minwidth=42, stretch=False, anchor="center")
        self.roster_tree.column("Participant", width=128, minwidth=120, stretch=True)
        self.roster_tree.column("Status", width=72, minwidth=68, stretch=False, anchor="center")
        self.roster_tree.column("Check-in", width=72, minwidth=68, stretch=False, anchor="center")
        
        self.roster_tree.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        
        scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.roster_tree.yview)
        self.roster_tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=3, column=2, sticky="ns", pady=(10, 0))

        btn_frame = tk.Frame(left_frame, bg=theme.PANEL)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(12, 2))
        
        theme.make_button(btn_frame, "Mark Present", lambda: self.mark_attendance("Present"), kind="primary").grid(row=0, column=0, padx=5)
        theme.make_button(btn_frame, "Mark Absent", lambda: self.mark_attendance("Absent"), kind="danger").grid(row=0, column=1, padx=5)

    def create_right_frame(self):
        right_frame = tk.Frame(self, bg=theme.BG, padx=14, pady=14,
                       highlightthickness=1, highlightbackground=theme.BORDER)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right_frame.grid_rowconfigure(2, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        theme.section_title(right_frame, "Attendance Records", bg=theme.BG).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        self.var_search = tk.StringVar()
        search_frame = theme.search_bar(
            right_frame, self.var_search, self.search_attendance,
            self.load_all_attendance, label="Filter:", entry_width=25)
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        cols = ("Att ID", "Event", "Session", "Participant", "Status", "Time")
        self.att_tree = ttk.Treeview(right_frame, columns=cols, show="headings")
        for col in cols:
            self.att_tree.heading(col, text=col)
        self.att_tree.column("Att ID", width=42, minwidth=40, stretch=False, anchor="center")
        self.att_tree.column("Event", width=125, minwidth=110, stretch=True)
        self.att_tree.column("Session", width=135, minwidth=120, stretch=True)
        self.att_tree.column("Participant", width=110, minwidth=100, stretch=True)
        self.att_tree.column("Status", width=70, minwidth=66, stretch=False, anchor="center")
        self.att_tree.column("Time", width=78, minwidth=74, stretch=False, anchor="center")
        
        self.att_tree.grid(row=2, column=0, sticky="nsew")
        
        scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.att_tree.yview)
        x_scroll = ttk.Scrollbar(right_frame, orient=tk.HORIZONTAL, command=self.att_tree.xview)
        self.att_tree.configure(yscrollcommand=scroll.set, xscrollcommand=x_scroll.set)
        scroll.grid(row=2, column=1, sticky="ns")
        x_scroll.grid(row=3, column=0, sticky="ew")

        theme.make_button(right_frame, "Delete Selected Record", self.delete_attendance, kind="danger").grid(row=4, column=0, pady=(10, 0), sticky="e")

    def load_events(self):
        conn = self.db.get_connection()
        if not conn: return
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT event_id, event_name FROM Event ORDER BY event_name")
            self.event_map.clear()
            for eid, ename in cursor.fetchall():
                self.event_map[ename] = eid
            self.combo_event['values'] = list(self.event_map.keys())
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading events:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def on_event_selected(self, event=None):
        ename = self.var_event.get()
        if not ename or ename not in self.event_map: return
        eid = self.event_map[ename]
        
        self.var_session.set("")
        self.combo_session['values'] = []
        self.session_map.clear()
        self.roster_tree.delete(*self.roster_tree.get_children())
        
        conn = self.db.get_connection()
        if not conn: return
        cursor = None
        try:
            cursor = conn.cursor()
            query = """
                SELECT s.session_id, s.session_title, s.session_date, s.start_time, s.end_time, v.venue_name
                FROM Session s
                JOIN Venue v ON s.venue_id = v.venue_id
                WHERE s.event_id = %s
                ORDER BY s.session_date, s.start_time
            """
            cursor.execute(query, (eid,))
            sessions = []
            for row in cursor.fetchall():
                sid = row[0]
                label = f"{row[1]} ({row[2]} {row[3]}-{row[4]} at {row[5]})"
                self.session_map[label] = sid
                sessions.append(label)
            self.combo_session['values'] = sessions
            
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading sessions:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def on_session_selected(self, event=None):
        self.load_roster()

    def load_roster(self):
        s_label = self.var_session.get()
        if not s_label or s_label not in self.session_map: return
        sid = self.session_map[s_label]
        
        ename = self.var_event.get()
        eid = self.event_map[ename]
        
        conn = self.db.get_connection()
        if not conn: return
        cursor = None
        try:
            self.roster_tree.delete(*self.roster_tree.get_children())
            cursor = conn.cursor()
            query = """
                SELECT r.registration_id, p.participant_name, a.attendance_status, a.check_in_time
                FROM Registration r
                JOIN Participant p ON r.participant_id = p.participant_id
                LEFT JOIN Attendance a ON r.registration_id = a.registration_id AND a.session_id = %s
                WHERE r.event_id = %s
                ORDER BY p.participant_name
            """
            cursor.execute(query, (sid, eid))
            for row in cursor.fetchall():
                status = row[2] if row[2] else "-"
                time = str(row[3]) if row[3] else "-"
                theme.insert_table_row(self.roster_tree, (row[0], row[1], status, time))
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading roster:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def mark_attendance(self, status):
        s_label = self.var_session.get()
        if not s_label or s_label not in self.session_map:
            messagebox.showerror("Error", "Please select a Session first.")
            return
            
        sid = self.session_map[s_label]
        
        selected = self.roster_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a participant from the roster.")
            return
            
        values = self.roster_tree.item(selected)['values']
        reg_id = values[0]
        
        conn = self.db.get_connection()
        if not conn: return
        cursor = None
        try:
            cursor = conn.cursor()
            
            # Verify participant is registered for this event (security check as requested)
            ename = self.var_event.get()
            eid = self.event_map[ename]
            cursor.execute("SELECT 1 FROM Registration WHERE registration_id=%s AND event_id=%s", (reg_id, eid))
            if not cursor.fetchone():
                messagebox.showerror("Error", "Selected participant is not registered for this event.")
                return
                
            check_in = datetime.datetime.now().strftime("%H:%M:%S") if status == "Present" else None
            
            # Check if record exists
            cursor.execute("SELECT attendance_id FROM Attendance WHERE registration_id=%s AND session_id=%s", (reg_id, sid))
            existing = cursor.fetchone()
            
            if existing:
                query = "UPDATE Attendance SET attendance_status=%s, check_in_time=%s WHERE attendance_id=%s"
                cursor.execute(query, (status, check_in, existing[0]))
            else:
                query = "INSERT INTO Attendance (registration_id, session_id, attendance_status, check_in_time) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (reg_id, sid, status, check_in))
                
            conn.commit()
            
            # Refresh both trees
            self.load_roster()
            self.load_all_attendance()
            
        except Error as e:
            messagebox.showerror("Database Error", f"Error marking attendance:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def fetch_attendance(self, query, params=None):
        conn = self.db.get_connection()
        if not conn: return
        cursor = None
        try:
            self.att_tree.delete(*self.att_tree.get_children())
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            for row in cursor.fetchall():
                time = str(row[5]) if row[5] else "-"
                theme.insert_table_row(self.att_tree, (row[0], row[1], row[2], row[3], row[4], time))
        except Error as e:
            messagebox.showerror("Database Error", f"Error fetching attendance:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def load_all_attendance(self):
        query = """
            SELECT a.attendance_id, e.event_name, s.session_title, p.participant_name, a.attendance_status, a.check_in_time
            FROM Attendance a
            JOIN Session s ON a.session_id = s.session_id
            JOIN Event e ON s.event_id = e.event_id
            JOIN Registration r ON a.registration_id = r.registration_id
            JOIN Participant p ON r.participant_id = p.participant_id
            ORDER BY a.attendance_id DESC
        """
        self.fetch_attendance(query)

    def search_attendance(self):
        term = self.var_search.get().strip()
        if not term:
            self.load_all_attendance()
            return
            
        s_term = f"%{term}%"
        query = """
            SELECT a.attendance_id, e.event_name, s.session_title, p.participant_name, a.attendance_status, a.check_in_time
            FROM Attendance a
            JOIN Session s ON a.session_id = s.session_id
            JOIN Event e ON s.event_id = e.event_id
            JOIN Registration r ON a.registration_id = r.registration_id
            JOIN Participant p ON r.participant_id = p.participant_id
            WHERE e.event_name LIKE %s OR s.session_title LIKE %s OR p.participant_name LIKE %s
            ORDER BY a.attendance_id DESC
        """
        self.fetch_attendance(query, (s_term, s_term, s_term))

    def delete_attendance(self):
        selected = self.att_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select an attendance record to delete.")
            return
            
        att_id = self.att_tree.item(selected)['values'][0]
        
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this attendance record?")
        if not confirm: return
        
        conn = self.db.get_connection()
        if not conn: return
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Attendance WHERE attendance_id=%s", (att_id,))
            conn.commit()
            messagebox.showinfo("Success", "Attendance record deleted successfully.")
            self.load_roster() # In case the deleted record belongs to the currently viewed roster
            self.load_all_attendance()
        except Error as e:
            messagebox.showerror("Database Error", f"Error deleting attendance:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
