import tkinter as tk
from tkinter import ttk, messagebox
from gui import theme
from database.db_connection import DatabaseConnection
from mysql.connector import Error

class DashboardScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=theme.BG)
        self.db = DatabaseConnection()

        outer = tk.Frame(self, bg=theme.BG, padx=28, pady=26)
        outer.pack(fill="both", expand=True)

        theme.page_header(
            outer, "Dashboard",
            "Overview of events, participants and registrations"
        ).pack(fill="x", pady=(0, 24))

        self.stats_frame = tk.Frame(outer, bg=theme.BG)
        self.stats_frame.pack(fill="x")
        self.stats_frame.grid_columnconfigure(0, weight=1, uniform="stat")
        self.stats_frame.grid_columnconfigure(1, weight=1, uniform="stat")
        self.stats_frame.grid_columnconfigure(2, weight=1, uniform="stat")

        self.lbl_events = self.create_stat_card(
            self.stats_frame, "Total Events", theme.PRIMARY, 0)
        self.lbl_participants = self.create_stat_card(
            self.stats_frame, "Total Participants", theme.SUCCESS, 1)
        self.lbl_registrations = self.create_stat_card(
            self.stats_frame, "Total Registrations", theme.WARNING, 2)

        workflow = tk.Frame(outer, bg=theme.BG)
        workflow.pack(fill="both", expand=True, pady=(38, 0))
        theme.form_section(workflow, "Event lifecycle", bg=theme.BG).pack(
            fill="x", pady=(0, 16))

        stages_frame = tk.Frame(workflow, bg=theme.BG)
        stages_frame.pack(fill="both", expand=True)
        stages_frame.grid_rowconfigure(1, weight=1)
        stages = (
            ("01", "Plan", "Events, sessions and venues"),
            ("02", "Operate", "Participants, registration and attendance"),
            ("03", "Close out", "Payments and certificates"),
        )
        for column, (number, title, description) in enumerate(stages):
            stages_frame.grid_columnconfigure(column, weight=1, uniform="stage")
            stage = tk.Frame(stages_frame, bg=theme.PANEL, padx=18, pady=20,
                             highlightthickness=1, highlightbackground=theme.BORDER)
            stage.grid(row=1, column=column, sticky="nsew",
                       padx=(0 if column == 0 else 8, 8 if column < 2 else 0))
            tk.Label(stage, text=number, bg=theme.PANEL, fg=theme.ACCENT,
                     font=theme.FONT_H2, anchor="w").pack(fill="x")
            tk.Label(stage, text=title, bg=theme.PANEL, fg=theme.BRAND,
                     font=theme.FONT_H1, anchor="w").pack(fill="x", pady=(8, 4))
            tk.Label(stage, text=description, bg=theme.PANEL, fg=theme.TEXT_MUTED,
                     font=theme.FONT_BODY, anchor="w", justify="left",
                     wraplength=220).pack(fill="x")

        self.load_statistics()

    def create_stat_card(self, parent, title, accent, col):
        card = tk.Frame(parent, bg=theme.PANEL, highlightthickness=1,
                        highlightbackground=theme.BORDER)
        card.grid(row=0, column=col, padx=9, pady=4, sticky="nsew")

        tk.Frame(card, bg=accent, height=4).pack(fill="x")

        body = tk.Frame(card, bg=theme.PANEL, padx=21, pady=20)
        body.pack(fill="both", expand=True)

        tk.Label(body, text=title, bg=theme.PANEL, fg=theme.TEXT_MUTED,
             font=theme.FONT_BODY_B, anchor="w").pack(fill="x")

        lbl_value = tk.Label(body, text="—", bg=theme.PANEL, fg=theme.BRAND,
                             font=theme.FONT_CARD, anchor="w")
        lbl_value.pack(fill="x", pady=(9, 0))

        return lbl_value

    def load_statistics(self):
        connection = self.db.get_connection()
        if connection is None:
            messagebox.showerror("Database Error", "Failed to connect to the database.\nPlease ensure MySQL/XAMPP is running.")
            self.lbl_events.config(text="Error")
            self.lbl_participants.config(text="Error")
            self.lbl_registrations.config(text="Error")
            return
            
        cursor = None
        try:
            cursor = connection.cursor()
            
            # Count Events
            cursor.execute("SELECT COUNT(*) FROM Event")
            total_events = cursor.fetchone()[0]
            
            # Count Participants
            cursor.execute("SELECT COUNT(*) FROM Participant")
            total_participants = cursor.fetchone()[0]
            
            # Count Registrations
            cursor.execute("SELECT COUNT(*) FROM Registration")
            total_registrations = cursor.fetchone()[0]
            
            self.lbl_events.config(text=str(total_events))
            self.lbl_participants.config(text=str(total_participants))
            self.lbl_registrations.config(text=str(total_registrations))
            
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to retrieve data:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
