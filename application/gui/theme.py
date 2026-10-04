"""EventFlow - shared visual theme (colors, fonts, ttk styles, widget helpers).

This module contains presentation-only code: colours, fonts, ttk style
configuration and small widget factories. It performs no database access and
implements no business or validation rules, so it cannot affect application
behaviour.
"""
import tkinter as tk
from tkinter import ttk


# ------------------------------------------------------------------ palette
BRAND          = "#91bce4"
BRAND_LIGHT    = "#bdd6ee"
SIDEBAR_BG     = "#101b28"
SIDEBAR_HOVER  = "#1b2c3d"
SIDEBAR_ACTIVE = "#285d8d"
SIDEBAR_TEXT   = "#d9e3ed"
SIDEBAR_MUTED  = "#9aabbd"

ACCENT         = "#3782bc"
BG             = "#121b25"
PANEL          = "#1b2733"
PANEL_ALT      = "#222f3c"
INPUT_BG       = "#202d39"
BORDER         = "#354454"
TEXT           = "#e3eaf1"
TEXT_MUTED     = "#a0afbf"
TEXT_ON_DARK   = "#f5f8fb"

PRIMARY   = "#347db5"
SECONDARY = "#475d72"
SUCCESS   = "#2c725e"
DANGER    = "#a94349"
WARNING   = "#80652f"
NEUTRAL   = "#3c4d5e"

# Hover shades add contrast without introducing a second accent palette.
PRIMARY_D   = "#438dc6"
SECONDARY_D = "#5a7187"
SUCCESS_D   = "#37876f"
DANGER_D    = "#c15359"
WARNING_D   = "#98783a"
NEUTRAL_D   = "#506276"

# ------------------------------------------------------------------ fonts
FAMILY      = "Segoe UI"
FONT_TITLE  = (FAMILY, 20, "bold")
FONT_H1     = (FAMILY, 14, "bold")
FONT_H2     = (FAMILY, 11, "bold")
FONT_BODY   = (FAMILY, 10)
FONT_BODY_B = (FAMILY, 10, "bold")
FONT_SMALL  = (FAMILY, 9)
FONT_CARD   = (FAMILY, 30, "bold")
FONT_BRAND  = (FAMILY, 16, "bold")
FONT_SUB    = (FAMILY, 8)

_KIND_COLORS = {
    "primary":   (PRIMARY, PRIMARY_D),
    "secondary": (SECONDARY, SECONDARY_D),
    "success":   (SUCCESS, SUCCESS_D),
    "danger":    (DANGER, DANGER_D),
    "warning":   (WARNING, WARNING_D),
    "neutral":   (NEUTRAL, NEUTRAL_D),
}


# ------------------------------------------------------------ ttk styling
def apply_theme(root):
    """Apply global fonts and ttk widget styles. Call once on the root window."""
    try:
        root.configure(bg=BG)
    except tk.TclError:
        pass

    # Default font for classic (tk) widgets that do not specify one explicitly.
    try:
        root.option_add("*Font", FONT_BODY)
        root.option_add("*TCombobox*Listbox.font", FONT_BODY)
        root.option_add("*Menu.font", FONT_BODY)
        root.option_add("*TCombobox*Listbox.background", INPUT_BG)
        root.option_add("*TCombobox*Listbox.foreground", TEXT)
        root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
        root.option_add("*TCombobox*Listbox.selectForeground", TEXT_ON_DARK)
        root.option_add("*Menu.background", PANEL)
        root.option_add("*Menu.foreground", TEXT)
        root.option_add("*Menu.activeBackground", ACCENT)
        root.option_add("*Menu.activeForeground", TEXT_ON_DARK)
    except tk.TclError:
        pass

    style = ttk.Style(root)
    try:
        style.theme_use("clam")          # flat, consistent cross-widget look
    except tk.TclError:
        pass

    # --- Tables ---------------------------------------------------------
    style.configure(
        "Treeview",
        font=FONT_BODY,
        rowheight=32,
        background=PANEL,
        fieldbackground=PANEL,
        foreground=TEXT,
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "Treeview.Heading",
        font=FONT_BODY_B,
        background=PANEL_ALT,
        foreground=TEXT,
        relief="flat",
        padding=(9, 9),
    )
    style.map("Treeview.Heading", background=[("active", "#304254")])
    style.map("Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", TEXT_ON_DARK)])

    # --- Combobox -------------------------------------------------------
    style.configure(
        "TCombobox",
        font=FONT_BODY,
        padding=(7, 6),
        fieldbackground=INPUT_BG,
        background=PANEL_ALT,
        foreground=TEXT,
        arrowcolor=BRAND,
    )
    style.map("TCombobox",
              fieldbackground=[("readonly", INPUT_BG)],
              foreground=[("readonly", TEXT)])
    style.map("TCombobox",
              selectbackground=[("readonly", ACCENT)],
              selectforeground=[("readonly", TEXT_ON_DARK)])

    # --- Scrollbars -----------------------------------------------------
    style.configure(
        "TScrollbar",
        background="#344455",
        troughcolor=BG,
        bordercolor=PANEL,
        arrowsize=11,
        arrowcolor=TEXT_MUTED,
    )
    style.map("TScrollbar", background=[("active", "#506276")])

    return style


# --------------------------------------------------------- widget factories
def make_button(parent, text, command=None, kind="primary", width=None, **kw):
    """Return a flat, themed tk.Button with a hover effect.

    kinds: primary, secondary, success, danger, warning, neutral
    """
    bg, bg_dark = _KIND_COLORS.get(kind, _KIND_COLORS["primary"])
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=TEXT_ON_DARK,
        activebackground=bg_dark, activeforeground=TEXT_ON_DARK,
        font=FONT_BODY_B, bd=0, relief="flat", cursor="hand2",
        padx=12, pady=5, **kw,
    )
    if width:
        btn.config(width=width)
    btn.bind("<Enter>", lambda _e: btn.config(bg=bg_dark))
    btn.bind("<Leave>", lambda _e: btn.config(bg=bg))
    return btn


def section_title(parent, text, bg=PANEL):
    """Return a styled section/form title Label."""
    return tk.Label(parent, text=text, bg=bg, fg=TEXT,
                    font=FONT_H1, anchor="w")


def field_label(parent, text, bg=PANEL):
    """Return a styled form field Label."""
    return tk.Label(parent, text=text, bg=bg, fg=TEXT,
                    font=FONT_BODY, anchor="w")


def panel_title(parent, text, bg=BG):
    """Return a bold label used above a table/list panel."""
    return tk.Label(parent, text=text, bg=bg, fg=BRAND,
                    font=FONT_H2, anchor="w")


def form_section(parent, text, bg=PANEL):
    """Return a compact section heading and divider for form groups."""
    section = tk.Frame(parent, bg=bg)
    tk.Label(section, text=text.upper(), bg=bg, fg=TEXT_MUTED,
             font=FONT_SMALL + ("bold",), anchor="w").pack(fill="x")
    tk.Frame(section, bg=BORDER, height=1).pack(fill="x", pady=(5, 0))
    return section


def page_header(parent, title, subtitle=None, bg=BG):
    """Return a Frame with a page title and optional subtitle."""
    header = tk.Frame(parent, bg=bg)
    tk.Label(header, text=title, bg=bg, fg=BRAND,
             font=FONT_TITLE, anchor="w").pack(anchor="w")
    if subtitle:
        tk.Label(header, text=subtitle, bg=bg, fg=TEXT_MUTED,
                 font=FONT_BODY, anchor="w").pack(anchor="w", pady=(2, 0))
    return header


def styled_entry(parent, textvariable=None, width=25, **kw):
    """Return a flat entry with a subtle focus highlight."""
    return tk.Entry(
        parent, textvariable=textvariable, width=width, font=FONT_BODY,
        bg=INPUT_BG, fg=TEXT, selectbackground=ACCENT,
        selectforeground=TEXT_ON_DARK,
        relief="flat", bd=0, insertbackground=TEXT,
        highlightthickness=1, highlightbackground=BORDER,
        highlightcolor=ACCENT, **kw,
    )


def insert_table_row(tree, values):
    """Insert a row with alternating presentation-only background tags."""
    tree.tag_configure("row_even", background=PANEL)
    tree.tag_configure("row_odd", background=PANEL_ALT)
    row_tag = "row_even" if len(tree.get_children("")) % 2 == 0 else "row_odd"
    return tree.insert("", tk.END, values=values, tags=(row_tag,))


def search_bar(parent, textvariable, on_search, on_show_all,
               label="Search:", bg=BG, entry_width=28):
    """Return a consistent search bar Frame (label + entry + two buttons)."""
    bar = tk.Frame(parent, bg=bg)
    tk.Label(bar, text=label, bg=bg, fg=TEXT, font=FONT_BODY).pack(
        side=tk.LEFT, padx=(0, 6))
    entry = styled_entry(bar, textvariable=textvariable, width=entry_width)
    entry.pack(side=tk.LEFT, ipady=3, padx=(0, 6))
    make_button(bar, "Search", on_search, kind="secondary").pack(
        side=tk.LEFT, padx=3)
    make_button(bar, "Show All", on_show_all, kind="neutral").pack(
        side=tk.LEFT, padx=3)
    return bar
