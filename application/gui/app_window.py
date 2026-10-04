import tkinter as tk
from tkinter import ttk
from . import theme
from .dashboard_screen import DashboardScreen
from .events_screen import EventsScreen
from .participants_screen import ParticipantsScreen
from .sessions_screen import SessionsScreen
from .registration_screen import RegistrationScreen
from .attendance_screen import AttendanceScreen
from .payments_screen import PaymentsScreen
from .certificates_screen import CertificatesScreen

class AppWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        theme.apply_theme(self)
        self.title("EventSync - Event Management System")
        self.geometry("1200x740")
        self.minsize(1024, 640)
        self.configure(bg=theme.BG)

        # Configure layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar_frame = tk.Frame(self, bg=theme.SIDEBAR_BG, width=210)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        self.content_frame = tk.Frame(self, bg=theme.BG)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.current_screen = None
        self.page_header_widget = None
        self.active_nav = None
        self.nav_items = {}

        self.create_sidebar()
        self.show_dashboard()

    def create_sidebar(self):
        sb = self.sidebar_frame

        # ---- Brand header -----------------------------------------------
        brand = tk.Frame(sb, bg=theme.SIDEBAR_BG)
        brand.pack(fill="x", padx=17, pady=(24, 20))
        mark = tk.Label(brand, text="ES", bg=theme.SIDEBAR_ACTIVE,
                fg=theme.TEXT_ON_DARK, font=(theme.FAMILY, 10, "bold"),
                width=3, height=2)
        mark.pack(anchor="w", pady=(0, 10))
        tk.Label(brand, text="EventSync", bg=theme.SIDEBAR_BG,
             fg=theme.TEXT_ON_DARK, font=theme.FONT_BRAND,
             anchor="w").pack(fill="x")
        tk.Label(brand, text="Event Management System",
             bg=theme.SIDEBAR_BG, fg=theme.SIDEBAR_MUTED,
             font=theme.FONT_SMALL, anchor="w").pack(fill="x", pady=(5, 0))

        tk.Frame(sb, bg=theme.SIDEBAR_HOVER, height=1).pack(
            fill="x", padx=16, pady=(0, 14))

        # ---- Navigation --------------------------------------------------
        nav = [
            ("dashboard",    "Dashboard",    self.show_dashboard),
            ("events",       "Events",       self.show_events),
            ("sessions",     "Sessions",     self.show_sessions),
            ("participants", "Participants", self.show_participants),
            ("registration", "Registration", self.show_registration),
            ("attendance",   "Attendance",   self.show_attendance),
            ("payments",     "Payments",     self.show_payments),
            ("certificates", "Certificates", self.show_certificates),
        ]
        for key, label, command in nav:
            self.nav_items[key] = self._nav_item(sb, key, label, command)

        tk.Label(sb, text="v1.0", bg=theme.SIDEBAR_BG, fg=theme.SIDEBAR_HOVER,
                 font=theme.FONT_SUB).pack(side="bottom", pady=14)

    def _nav_item(self, parent, key, label, command):
        row = tk.Frame(parent, bg=theme.SIDEBAR_BG)
        row.pack(fill="x", padx=9, pady=2)
        bar = tk.Frame(row, bg=theme.SIDEBAR_BG, width=4)
        bar.pack(side="left", fill="y")
        btn = tk.Button(row, text="   " + label, command=command,
                        bg=theme.SIDEBAR_BG, fg=theme.SIDEBAR_TEXT,
                        activebackground=theme.SIDEBAR_HOVER,
                        activeforeground=theme.TEXT_ON_DARK,
                        font=theme.FONT_BODY, bd=0, relief="flat",
                        anchor="w", cursor="hand2", padx=10, pady=8)
        btn.pack(side="left", fill="x", expand=True)
        btn.bind("<Enter>", lambda _e: self._hover_nav(key, True))
        btn.bind("<Leave>", lambda _e: self._hover_nav(key, False))
        return {"row": row, "bar": bar, "btn": btn}

    def _hover_nav(self, key, entering):
        if key == self.active_nav:
            return
        item = self.nav_items.get(key)
        if not item:
            return
        color = theme.SIDEBAR_HOVER if entering else theme.SIDEBAR_BG
        item["row"].config(bg=color)
        item["btn"].config(bg=color)

    def _set_active(self, key):
        self.active_nav = key
        for k, item in self.nav_items.items():
            if k == key:
                item["row"].config(bg=theme.SIDEBAR_ACTIVE)
                item["bar"].config(bg=theme.TEXT_ON_DARK)
                item["btn"].config(bg=theme.SIDEBAR_ACTIVE,
                                   fg=theme.TEXT_ON_DARK, font=theme.FONT_BODY_B)
            else:
                item["row"].config(bg=theme.SIDEBAR_BG)
                item["bar"].config(bg=theme.SIDEBAR_BG)
                item["btn"].config(bg=theme.SIDEBAR_BG,
                                   fg=theme.SIDEBAR_TEXT, font=theme.FONT_BODY)

    def show_dashboard(self):
        self._show_screen(DashboardScreen, "dashboard")

    def show_events(self):
        self._show_screen(EventsScreen, "events")

    def show_sessions(self):
        self._show_screen(SessionsScreen, "sessions")

    def show_participants(self):
        self._show_screen(ParticipantsScreen, "participants")

    def show_registration(self):
        self._show_screen(RegistrationScreen, "registration")

    def show_attendance(self):
        self._show_screen(AttendanceScreen, "attendance")

    def show_payments(self):
        self._show_screen(PaymentsScreen, "payments")

    def show_certificates(self):
        self._show_screen(CertificatesScreen, "certificates")

    def _show_screen(self, screen_class, nav_key):
        if self.current_screen is not None:
            self.current_screen.destroy()
        if self.page_header_widget is not None:
            self.page_header_widget.destroy()
            self.page_header_widget = None

        page_details = {
            "events": ("Events", "Create and maintain event details"),
            "sessions": ("Sessions", "Schedule sessions and venues"),
            "participants": ("Participants", "Manage the participant directory"),
            "registration": ("Registration", "Manage registrations and the waitlist"),
            "attendance": ("Attendance", "Record and review session attendance"),
            "payments": ("Payments", "Track registration payments"),
            "certificates": ("Certificates", "Review eligibility and certificates"),
        }
        if nav_key in page_details:
            title, subtitle = page_details[nav_key]
            self.page_header_widget = theme.page_header(
                self.content_frame, title, subtitle)
            self.page_header_widget.pack(fill="x", padx=24, pady=(18, 6))

        self.current_screen = screen_class(self.content_frame)
        self.current_screen.pack(fill="both", expand=True, padx=0, pady=(0, 8))
        self._set_active(nav_key)
