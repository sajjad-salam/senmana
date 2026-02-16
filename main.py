import requests
import json
import time
import base64
import hashlib
import hmac
import os
from uuid import uuid4
import urllib3
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
from urllib.parse import urlparse, parse_qsl, urlencode, unquote

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

RAW_SECRET_KEY = "76iRl07s0xSN9jqmEWAt79EBJZulIQIsV64FZr2O"
REAL_SECRET_BYTES = base64.b64decode(RAW_SECRET_KEY)


class AsianPlayerDownloader:
    # Light theme colors
    LIGHT_BG = "#f1f5f9"
    LIGHT_CARD = "#ffffff"
    LIGHT_TEXT = "#0f172a"
    LIGHT_TEXT_SEC = "#475569"
    LIGHT_BORDER = "#cbd5e1"
    LIGHT_INPUT = "#f8fafc"
    LIGHT_SHADOW = "#94a3b8"

    # Dark theme colors
    DARK_BG = "#0f172a"
    DARK_CARD = "#1e293b"
    DARK_TEXT = "#f1f5f9"
    DARK_TEXT_SEC = "#94a3b8"
    DARK_BORDER = "#334155"
    DARK_INPUT = "#334155"
    DARK_SHADOW = "#000000"

    # Semantic colors (work for both themes)
    ACCENT = "#6366f1"
    ACCENT_HOVER = "#4f46e5"
    ACCENT_LIGHT = "#818cf8"
    SUCCESS = "#10b981"
    SUCCESS_LIGHT = "#34d399"
    WARNING = "#f59e0b"
    WARNING_LIGHT = "#fbbf24"
    ERROR = "#ef4444"
    ERROR_LIGHT = "#f87171"
    INFO = "#3b82f6"

    # Gradients
    GRADIENT_START = "#6366f1"
    GRADIENT_END = "#8b5cf6"

    def __init__(self, root):
        self.root = root
        self.root.title("تحميل من Asian Player")
        self.root.geometry("1100x750")
        self.root.resizable(True, True)

        # Theme state - initialize first before any UI
        self.dark_mode = False

        # App state
        self.auth_token = None
        self.x_user = None
        self.search_results = []
        self.selected_subject = None
        self.download_links = []
        self.episodes_data = []
        self.seasons_data = {}
        self.downloading = False
        self.stop_download = False
        self.episode_checkboxes = {}

        # Initialize theme colors BEFORE setup_ui
        self.update_theme_colors()

        # Setup UI
        self.setup_ui()

        # Auto-authenticate on startup
        self.root.after(500, self.authenticate)

    def update_theme_colors(self):
        """Update color constants based on current theme"""
        # Light theme colors
        light_bg = "#f1f5f9"
        light_card = "#ffffff"
        light_text = "#0f172a"
        light_text_sec = "#475569"
        light_border = "#cbd5e1"
        light_input = "#f8fafc"
        light_shadow = "#94a3b8"

        # Dark theme colors
        dark_bg = "#0f172a"
        dark_card = "#1e293b"
        dark_text = "#f1f5f9"
        dark_text_sec = "#94a3b8"
        dark_border = "#334155"
        dark_input = "#334155"
        dark_shadow = "#000000"

        if self.dark_mode:
            self.BG = dark_bg
            self.CARD = dark_card
            self.TEXT = dark_text
            self.TEXT_SEC = dark_text_sec
            self.BORDER = dark_border
            self.INPUT_BG = dark_input
            self.SHADOW = dark_shadow
            self.SCROLLBAR_BG = dark_card
            self.SCROLLBAR_FG = dark_border
        else:
            self.BG = light_bg
            self.CARD = light_card
            self.TEXT = light_text
            self.TEXT_SEC = light_text_sec
            self.BORDER = light_border
            self.INPUT_BG = light_input
            self.SHADOW = light_shadow
            self.SCROLLBAR_BG = light_card
            self.SCROLLBAR_FG = light_border

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.dark_mode = not self.dark_mode
        self.update_theme_colors()
        self.refresh_ui_theme()

    def refresh_ui_theme(self):
        """Refresh all UI elements with current theme colors"""
        # Update main container
        if hasattr(self, 'main_container'):
            self.main_container.config(bg=self.BG)

        # Update header
        if hasattr(self, 'header'):
            self.header.config(bg=self.ACCENT)

        # Update status bar
        if hasattr(self, 'status_bar'):
            self.status_bar.config(bg=self.CARD, fg=self.TEXT_SEC)

        # Update all frames and labels recursively
        self.update_widget_colors(self.main_container)

    def update_widget_colors(self, widget):
        """Recursively update widget colors based on theme"""
        try:
            widget_class = widget.winfo_class()

            if widget_class == 'Frame':
                widget.config(bg=self.BG if widget == self.main_container else self.CARD)
            elif widget_class == 'Label':
                # Check if it's a status label with special color
                current_bg = widget.cget('bg')
                if current_bg not in [self.SUCCESS, self.WARNING, self.ERROR]:
                    if widget == self.auth_status_label or 'status' in str(widget):
                        pass  # Keep status indicator colors
                    else:
                        widget.config(bg=self.CARD, fg=self.TEXT)
            elif widget_class == 'Button':
                # Skip theme toggle button and buttons with special colors
                if not hasattr(widget, '_is_theme_btn'):
                    current_bg = widget.cget('bg')
                    if current_bg == self.ACCENT or current_bg == self.ACCENT_HOVER or current_bg == self.SUCCESS or current_bg == self.WARNING:
                        pass  # Keep accent colors
                    elif current_bg == self.BORDER:
                        pass  # Keep border color
                    else:
                        widget.config(bg=self.ACCENT, fg='white')
            elif widget_class == 'Entry':
                widget.config(bg=self.INPUT_BG, fg=self.TEXT, insertbackground=self.ACCENT)
            elif widget_class == 'TCombobox':
                widget.config(bg=self.INPUT_BG, fg=self.TEXT)
            elif widget_class == 'Listbox':
                widget.config(bg=self.INPUT_BG, fg=self.TEXT, selectbackground=self.ACCENT, selectforeground='white')
            elif widget_class == 'Checkbutton':
                widget.config(bg=self.CARD, fg=self.TEXT, activebackground=self.ACCENT)
            elif widget_class == 'Canvas':
                widget.config(bg=self.CARD, highlightbackground=self.BORDER)
            elif widget_class == 'TNotebook':
                widget.config(bg=self.BG)
            elif widget_class == 'TProgressbar':
                widget.config(style=f'{".!theme" if self.dark_mode else ""}.Horizontal.TProgressbar')
            elif widget_class == 'Text':
                if widget != self.output_text:
                    widget.config(bg=self.INPUT_BG, fg=self.TEXT)
                else:
                    widget.config(bg=self.INPUT_BG, fg=self.TEXT, insertbackground=self.ACCENT)

        except Exception:
            pass  # Skip widgets that don't support these options

        # Recursively update children
        for child in widget.winfo_children():
            self.update_widget_colors(child)

    def __init__(self, root):
        self.root = root
        self.root.title("تحميل من Asian Player")
        self.root.geometry("1100x750")
        self.root.resizable(True, True)

        # Theme state - must be initialized BEFORE setup_ui
        self.dark_mode = False

        # App state
        self.auth_token = None
        self.x_user = None
        self.search_results = []
        self.selected_subject = None
        self.download_links = []
        self.episodes_data = []
        self.seasons_data = {}
        self.downloading = False
        self.stop_download = False
        self.episode_checkboxes = {}

        # Initialize theme colors BEFORE setup_ui
        self.update_theme_colors()

        # Setup UI
        self.setup_ui()

        # Auto-authenticate on startup
        self.root.after(500, self.authenticate)

    def setup_ui(self):
        """Build enhanced modern UI with improved styling"""
        # Configure root
        self.root.configure(bg=self.BG)

        # Main container
        self.main_container = tk.Frame(self.root, bg=self.BG)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Enhanced header with gradient-like effect and search bar
        self.header = tk.Frame(self.main_container, bg=self.ACCENT, height=90)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)

        header_content = tk.Frame(self.header, bg=self.ACCENT)
        header_content.pack(fill=tk.BOTH, expand=True, padx=25, pady=18)

        # Left side: Search bar with enhanced styling
        search_frame = tk.Frame(header_content, bg=self.ACCENT)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.search_entry_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_entry_var,
            font=("Segoe UI", 11),
            bg=self.LIGHT_CARD if not self.dark_mode else self.DARK_INPUT,
            fg=self.TEXT,
            insertbackground=self.ACCENT,
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightcolor=self.ACCENT_LIGHT,
            highlightbackground=self.BORDER,
            width=35
        )
        self.search_entry.pack(side=tk.RIGHT, padx=(0, 12), ipady=8, ipadx=15)
        self.search_entry.bind("<Return>", lambda e: self.search_content())
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.config(highlightcolor=self.ACCENT_LIGHT, highlightbackground=self.ACCENT))
        self.search_entry.bind("<FocusOut>", lambda e: self.search_entry.config(highlightbackground=self.BORDER))

        self.search_button = tk.Button(
            search_frame,
            text="🔍 بحث",
            command=self.search_content,
            bg=self.SUCCESS,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=24,
            pady=10,
            cursor="hand2",
            relief="flat",
            borderwidth=0,
            activebackground=self.SUCCESS_LIGHT
        )
        self.search_button.pack(side=tk.LEFT)

        # Right side: Title, theme toggle, and auth status
        right_frame = tk.Frame(header_content, bg=self.ACCENT)
        right_frame.pack(side=tk.RIGHT)

        # Theme toggle button
        self.theme_button = tk.Button(
            right_frame,
            text="🌙",
            command=self.toggle_theme,
            bg=self.ACCENT_HOVER,
            fg="white",
            font=("Segoe UI", 12),
            padx=10,
            pady=6,
            cursor="hand2",
            relief="flat",
            borderwidth=0,
            activebackground=self.ACCENT_LIGHT
        )
        self.theme_button._is_theme_btn = True
        self.theme_button.pack(side=tk.RIGHT, padx=(8, 0))

        title_label = tk.Label(
            right_frame,
            text="تحميل من Asian Player",
            font=("Segoe UI", 17, "bold"),
            bg=self.ACCENT,
            fg="white"
        )
        title_label.pack(side=tk.RIGHT, padx=12)

        # Enhanced auth status indicator with better styling
        self.auth_status_label = tk.Label(
            right_frame,
            text="جاري المصادقة...",
            font=("Segoe UI", 10, "bold"),
            bg=self.WARNING,
            fg="white",
            padx=14,
            pady=6,
            relief="flat",
            borderwidth=0
        )
        self.auth_status_label.pack(side=tk.RIGHT, padx=6)

        # Left side: Search bar
        search_frame = tk.Frame(header_content, bg=self.ACCENT)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.search_entry_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_entry_var,
            font=("Segoe UI", 11),
            bg=self.CARD,
            fg=self.TEXT,
            insertbackground=self.ACCENT,
            relief="flat",
            width=30
        )
        self.search_entry.pack(side=tk.RIGHT, padx=(0, 10), ipady=6, ipadx=12)
        self.search_entry.bind("<Return>", lambda e: self.search_content())

        self.search_button = tk.Button(
            search_frame,
            text="🔍 بحث",
            command=self.search_content,
            bg=self.SUCCESS,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=8,
            cursor="hand2",
            relief="flat",
            borderwidth=0
        )
        self.search_button.pack(side=tk.LEFT)

        # Right side: Title and auth status
        right_frame = tk.Frame(header_content, bg=self.ACCENT)
        right_frame.pack(side=tk.RIGHT)

        title_label = tk.Label(
            right_frame,
            text="تحميل من Asian Player",
            font=("Segoe UI", 16, "bold"),
            bg=self.ACCENT,
            fg="white"
        )
        title_label.pack(side=tk.RIGHT, padx=10)

        # Auth status indicator
        self.auth_status_label = tk.Label(
            right_frame,
            text="جاري المصادقة...",
            font=("Segoe UI", 10),
            bg=self.WARNING,
            fg="white",
            padx=12,
            pady=4
        )
        self.auth_status_label.pack(side=tk.RIGHT, padx=5)

        # Main content area with enhanced spacing
        content_container = tk.Frame(self.main_container, bg=self.BG)
        content_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=(20, 0))

        # Create enhanced sections
        self.create_search_results_section(content_container)
        self.create_episodes_section(content_container)
        self.create_downloads_section(content_container)

        # Enhanced status bar with better styling
        self.status_bar = tk.Label(
            self.main_container,
            text="● جاهز",
            font=("Segoe UI", 9),
            bg=self.CARD,
            fg=self.TEXT_SEC,
            anchor=tk.W,
            padx=20,
            pady=12
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=0, pady=(0, 0))

    def create_search_results_section(self, parent):
        """Create enhanced search results section with improved card design"""
        # Outer container for shadow effect
        shadow_container = tk.Frame(parent, bg=self.BG)
        shadow_container.pack(fill=tk.BOTH, expand=True, pady=(0, 18))

        # Shadow frame (simulated with border)
        shadow_frame = tk.Frame(shadow_container, bg=self.SHADOW if not self.dark_mode else self.BG)
        shadow_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 3), pady=(0, 3))

        # Main card
        card = tk.Frame(shadow_container, bg=self.CARD, highlightbackground=self.BORDER, highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        # Enhanced header with icon
        header = tk.Frame(card, bg=self.CARD)
        header.pack(fill=tk.X, padx=18, pady=(16, 12))

        # Section title with icon
        title_frame = tk.Frame(header, bg=self.CARD)
        title_frame.pack(side=tk.RIGHT)

        tk.Label(
            title_frame,
            text="🔍",
            font=("Segoe UI", 14),
            bg=self.CARD,
            fg=self.ACCENT
        ).pack(side=tk.RIGHT, padx=(0, 8))

        tk.Label(
            title_frame,
            text="نتائج البحث",
            font=("Segoe UI", 14, "bold"),
            bg=self.CARD,
            fg=self.TEXT
        ).pack(side=tk.RIGHT)

        # Divider
        divider = tk.Frame(card, bg=self.BORDER, height=1)
        divider.pack(fill=tk.X, padx=18, pady=(0, 12))

        # Selected content info with enhanced styling
        self.selected_info_frame = tk.Frame(card, bg=self.INPUT_BG)
        self.selected_info_frame.pack(fill=tk.X, padx=18, pady=(0, 12))

        tk.Label(
            self.selected_info_frame,
            text="المحتوى المختار:",
            font=("Segoe UI", 10, "bold"),
            bg=self.INPUT_BG,
            fg=self.TEXT_SEC
        ).pack(side=tk.RIGHT, padx=(0, 10), pady=8)

        self.title_label = tk.Label(
            self.selected_info_frame,
            text="-",
            font=("Segoe UI", 10, "bold"),
            bg=self.INPUT_BG,
            fg=self.ACCENT
        )
        self.title_label.pack(side=tk.RIGHT, pady=8)

        self.type_label = tk.Label(
            self.selected_info_frame,
            text="-",
            font=("Segoe UI", 9),
            bg=self.INPUT_BG,
            fg=self.TEXT_SEC
        )
        self.type_label.pack(side=tk.RIGHT, padx=(12, 0), pady=8)

        # Enhanced results list
        results_frame = tk.Frame(card, bg=self.CARD)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 16))

        scrollbar = tk.Scrollbar(results_frame, bg=self.CARD, troughcolor=self.INPUT_BG,
                                 highlightthickness=0, borderwidth=0)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        self.results_listbox = tk.Listbox(
            results_frame,
            font=("Segoe UI", 11),
            bg=self.INPUT_BG,
            fg=self.TEXT,
            selectbackground=self.ACCENT,
            selectforeground="white",
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            highlightcolor=self.ACCENT,
            yscrollcommand=scrollbar.set
        )
        self.results_listbox.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_listbox.yview)
        self.results_listbox.bind("<<ListboxSelect>>", self.on_result_select)

    def create_episodes_section(self, parent):
        """Create enhanced episodes selection section"""
        # Outer container for shadow effect
        shadow_container = tk.Frame(parent, bg=self.BG)
        shadow_container.pack(fill=tk.BOTH, expand=True, pady=(0, 18))

        # Shadow frame
        shadow_frame = tk.Frame(shadow_container, bg=self.SHADOW if not self.dark_mode else self.BG)
        shadow_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 3), pady=(0, 3))

        # Main card
        card = tk.Frame(shadow_container, bg=self.CARD, highlightbackground=self.BORDER, highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        # Enhanced header with icon and controls
        header = tk.Frame(card, bg=self.CARD)
        header.pack(fill=tk.X, padx=18, pady=(16, 12))

        # Section title with icon
        title_frame = tk.Frame(header, bg=self.CARD)
        title_frame.pack(side=tk.RIGHT)

        tk.Label(
            title_frame,
            text="📺",
            font=("Segoe UI", 14),
            bg=self.CARD,
            fg=self.ACCENT
        ).pack(side=tk.RIGHT, padx=(0, 8))

        tk.Label(
            title_frame,
            text="اختيار الحلقات",
            font=("Segoe UI", 14, "bold"),
            bg=self.CARD,
            fg=self.TEXT
        ).pack(side=tk.RIGHT)

        # Enhanced controls with better styling
        controls = tk.Frame(header, bg=self.CARD)
        controls.pack(side=tk.LEFT)

        # Selected count badge
        count_frame = tk.Frame(controls, bg=self.INPUT_BG)
        count_frame.pack(side=tk.LEFT, padx=(0, 12))

        tk.Label(
            count_frame,
            text="المحدد:",
            font=("Segoe UI", 9),
            bg=self.INPUT_BG,
            fg=self.TEXT_SEC
        ).pack(side=tk.RIGHT, padx=(0, 6))

        self.selected_count_label = tk.Label(
            count_frame,
            text="0",
            font=("Segoe UI", 10, "bold"),
            bg=self.ACCENT,
            fg="white",
            width=3,
            padx=6,
            pady=2
        )
        self.selected_count_label.pack(side=tk.RIGHT)

        # Select buttons with enhanced styling
        tk.Button(
            controls,
            text="✓ تحديد الكل",
            command=self.select_all_episodes,
            bg=self.ACCENT_HOVER,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=6,
            cursor="hand2",
            relief="flat",
            borderwidth=0,
            activebackground=self.ACCENT
        ).pack(side=tk.RIGHT, padx=3)

        tk.Button(
            controls,
            text="✗ إلغاء",
            command=self.deselect_all_episodes,
            bg=self.INPUT_BG,
            fg=self.TEXT,
            font=("Segoe UI", 9),
            padx=12,
            pady=6,
            cursor="hand2",
            relief="flat",
            borderwidth=1,
            highlightbackground=self.BORDER,
            activebackground=self.BORDER
        ).pack(side=tk.RIGHT, padx=3)

        # Resolution selector
        tk.Label(
            controls,
            text="الجودة:",
            font=("Segoe UI", 9, "bold"),
            bg=self.CARD,
            fg=self.TEXT_SEC
        ).pack(side=tk.RIGHT, padx=(0, 6))

        self.resolution_var = tk.StringVar(value="0")
        self.resolution_combo = ttk.Combobox(
            controls,
            textvariable=self.resolution_var,
            width=8,
            state="readonly",
            font=("Segoe UI", 9)
        )
        self.resolution_combo['values'] = ("الافتراضي", "360p", "480p", "720p", "1080p")
        self.resolution_combo.pack(side=tk.RIGHT, padx=(0, 12))
        self.resolution_combo.bind("<<ComboboxSelected>>", lambda e: self.load_season_episodes())

        # Season selector
        tk.Label(
            controls,
            text="الموسم:",
            font=("Segoe UI", 9, "bold"),
            bg=self.CARD,
            fg=self.TEXT_SEC
        ).pack(side=tk.RIGHT, padx=(0, 6))

        self.season_var = tk.StringVar(value="1")
        self.season_combo = ttk.Combobox(
            controls,
            textvariable=self.season_var,
            width=6,
            state="readonly",
            font=("Segoe UI", 9)
        )
        self.season_combo.pack(side=tk.RIGHT, padx=(0, 12))
        self.season_combo.bind("<<ComboboxSelected>>", lambda e: self.load_season_episodes())

        # Load button
        tk.Button(
            controls,
            text="🔄",
            command=self.load_season_episodes,
            bg=self.ACCENT,
            fg="white",
            font=("Segoe UI", 10),
            padx=12,
            pady=7,
            cursor="hand2",
            relief="flat",
            borderwidth=0,
            activebackground=self.ACCENT_LIGHT
        ).pack(side=tk.RIGHT, padx=(0, 8))

        # Enhanced episodes list with better styling
        episodes_container = tk.Frame(card, bg=self.CARD)
        episodes_container.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 16))

        self.episodes_canvas = tk.Canvas(
            episodes_container,
            bg=self.CARD,
            highlightthickness=0
        )
        ep_scrollbar = ttk.Scrollbar(
            episodes_container, orient=tk.VERTICAL, command=self.episodes_canvas.yview)
        self.episodes_canvas.configure(yscrollcommand=ep_scrollbar.set)

        self.episodes_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ep_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.episodes_inner_frame = tk.Frame(self.episodes_canvas, bg=self.CARD)
        self.episodes_canvas.create_window(
            (0, 0), window=self.episodes_inner_frame, anchor=tk.NW)

        self.episodes_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.episodes_inner_frame.bind("<Configure>", lambda e: self.episodes_canvas.configure(
            scrollregion=self.episodes_canvas.bbox("all")))

    def create_downloads_section(self, parent):
        """Create enhanced downloads and actions section"""
        # Outer container for shadow effect
        shadow_container = tk.Frame(parent, bg=self.BG)
        shadow_container.pack(fill=tk.BOTH, expand=True)

        # Shadow frame
        shadow_frame = tk.Frame(shadow_container, bg=self.SHADOW if not self.dark_mode else self.BG)
        shadow_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 3), pady=(0, 3))

        # Main card
        card = tk.Frame(shadow_container, bg=self.CARD, highlightbackground=self.BORDER, highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        # Enhanced header with icon
        header = tk.Frame(card, bg=self.CARD)
        header.pack(fill=tk.X, padx=18, pady=(16, 12))

        # Section title with icon
        title_frame = tk.Frame(header, bg=self.CARD)
        title_frame.pack(side=tk.RIGHT)

        tk.Label(
            title_frame,
            text="⬇️",
            font=("Segoe UI", 14),
            bg=self.CARD,
            fg=self.ACCENT
        ).pack(side=tk.RIGHT, padx=(0, 8))

        tk.Label(
            title_frame,
            text="التحميل والسجل",
            font=("Segoe UI", 14, "bold"),
            bg=self.CARD,
            fg=self.TEXT
        ).pack(side=tk.RIGHT)

        # Enhanced action buttons
        actions = tk.Frame(header, bg=self.CARD)
        actions.pack(side=tk.LEFT)

        # Download button
        tk.Button(
            actions,
            text="⬇️ تحميل",
            command=self.start_batch_download,
            bg=self.WARNING,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=18,
            pady=7,
            cursor="hand2",
            relief="flat",
            borderwidth=0,
            activebackground=self.WARNING_LIGHT
        ).pack(side=tk.RIGHT, padx=4)

        # Save button
        tk.Button(
            actions,
            text="💾 حفظ",
            command=self.save_urls_to_file,
            bg=self.SUCCESS,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=18,
            pady=7,
            cursor="hand2",
            relief="flat",
            borderwidth=0,
            activebackground=self.SUCCESS_LIGHT
        ).pack(side=tk.RIGHT, padx=4)

        # Links button
        tk.Button(
            actions,
            text="📋 الروابط",
            command=self.get_selected_links,
            bg=self.ACCENT,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=18,
            pady=7,
            cursor="hand2",
            relief="flat",
            borderwidth=0,
            activebackground=self.ACCENT_LIGHT
        ).pack(side=tk.RIGHT, padx=4)

        # Enhanced folder path selector
        folder_frame = tk.Frame(header, bg=self.INPUT_BG)
        folder_frame.pack(side=tk.LEFT, padx=(12, 0))

        tk.Label(
            folder_frame,
            text="📁",
            font=("Segoe UI", 10),
            bg=self.INPUT_BG,
            fg=self.TEXT_SEC
        ).pack(side=tk.RIGHT, padx=(6, 4))

        self.save_path_var = tk.StringVar(value=os.path.join(os.getcwd(), "downloads"))
        save_entry = ttk.Entry(
            folder_frame,
            textvariable=self.save_path_var,
            width=18,
            font=("Segoe UI", 9)
        )
        save_entry.pack(side=tk.RIGHT, padx=(0, 4))

        tk.Button(
            folder_frame,
            text="···",
            command=self.browse_folder,
            bg=self.BORDER,
            fg=self.TEXT,
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=5,
            cursor="hand2",
            relief="flat",
            borderwidth=0,
            activebackground=self.TEXT_SEC
        ).pack(side=tk.RIGHT, padx=(6, 6))

        # Enhanced output log with better styling
        log_container = tk.Frame(card, bg=self.INPUT_BG)
        log_container.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 16))

        self.output_text = scrolledtext.ScrolledText(
            log_container,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg=self.INPUT_BG,
            fg=self.TEXT,
            insertbackground=self.ACCENT,
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            highlightcolor=self.ACCENT,
            height=6
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling for episodes canvas"""
        self.episodes_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def log(self, message):
        """Add enhanced message to output text area"""
        # Add timestamp for better tracking
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()

    def set_status(self, status):
        """Update status bar with enhanced styling"""
        # Add status icon based on content
        if "✓" in status or "تم" in status:
            icon = "✓"
        elif "✗" in status or "فشل" in status or "خطأ" in status:
            icon = "✗"
        elif "جاري" in status:
            icon = "⟳"
        elif "🔍" in status or "بحث" in status:
            icon = "🔍"
        elif "🔐" in status or "مصادقة" in status:
            icon = "🔐"
        elif "📡" in status or "تحميل" in status:
            icon = "📡"
        else:
            icon = "●"

        self.status_bar.config(text=f"{icon} {status}")

    def get_auth_headers(self, method, path, timestamp, accept_val, content_type_val, content_length_val, body_md5):
        """Generate authentication headers"""
        sign_string = f"{method}\n{accept_val}\n{content_type_val}\n{content_length_val}\n{timestamp}\n{body_md5}\n{path}"
        signature_bytes = hmac.new(
            REAL_SECRET_BYTES, sign_string.encode('utf-8'), hashlib.md5).digest()
        signature_base64 = base64.b64encode(signature_bytes).decode('utf-8')
        final_header = f"{timestamp}|2|{signature_base64}"
        return final_header

    def authenticate(self):
        """Authenticate with the API"""
        def auth_thread():
            try:
                self.set_status("🔐 جاري المصادقة...")
                self.log("🔐 جاري المصادقة...")

                uid = str(uuid4())
                URL = "https://api3.aoneroom.com/wefeed-mobile-bff/app/config?keys=sa_trending_use_cache%2Croom_entrance_enable%2Csa_home_show_honor_v2%2Cpost_list_use_cache%2Csa_home_show_gamelist%2Csa_novel_icon_config%2Csa_search_guide%2Csa_lo_place_key%2Croom_cache_open%2Croom_cache_dialog_desc%2Csa_lo_place_api%2Csa_detail_for_you_insert_posts%2Csa_restrict_tips%2Csa_for_you_request_count%2Csa_post_exposure_percent%2Csa_data_operator_config%2Cpk_player_ui_key%2Csb_lv_play_timeout%2Csa_for_you_mode%2Cshorts_unlock_config%2Csa_post_video_auto_play%2Csb_lv_play_timeout_dp%2Cmine_notice_config_key%2Cfree_buy_config%2Csa_use_server_place%2Csa_pip_enable_memory%2Csa_show_no_subtitle_tips%2Csubtitle_search_opensub%2Csubtitle_language%2Cwidget_guide_enable%2Ckey_total_show_times%2CdownloadNewRange%2Ckey_storage_per_total_show_times%2CdownloadInCoroutine%2Csb_show_save_to%2Csb_battery_interval_day%2Ctransfer_share_link_url%2Csa_notification_refresh%2Csa_toolbar_notice%2Csa_dauupupup_config%2Cpush_pic_type_config%2Cpush_remind_notification_time%2Cpush_permanent_ui_ab_config%2Cpull_notification_deadline%2Csb_player_type%2ClowMemoryValue%2Cdownload_buffer_size%2Csa_history_lines_double%2CkeyAliveOff%2CkeyBackgroundReportOff%2CclientLogsRetrieve%2Cdownload_error_opt_off%2Cplayer_async%2CdownloadRangeSize%2Capp_center_switch%2Cplay_mode%2Cshorts_tab_in_for_you%2CvipFissionOn&version="

                parsed = urlparse(URL)
                params = dict(parse_qsl(parsed.query))
                sorted_query_encoded = urlencode(sorted(params.items()))
                sorted_query_for_sign = unquote(sorted_query_encoded)
                path_for_sign = f"{parsed.path}?{sorted_query_for_sign}"

                method = "GET"
                timestamp = str(int(time.time() * 1000))
                accept_val = "application/json"
                content_type_val = ""
                content_length_val = ""
                body_md5 = ""

                final_header = self.get_auth_headers(
                    method, path_for_sign, timestamp, accept_val, content_type_val, content_length_val, body_md5)

                headers = {
                    'User-Agent': "com.community.oneroom/50020075 (Linux; U; Android 12; ar_AE; SM-A025F; Build/SP1A.210812.016; Cronet/144.0.7509.3)",
                    'x-play-mode': "1",
                    'accept': "application/json",
                    'x-family-mode': "0",
                    'x-client-info': f'{{"package_name":"com.community.oneroom","version_name":"3.0.10.1110.03","version_code":50020075,"os":"android","os_version":"12","device_id":"58ceaf381245d06ca831d38f7285f50c","install_store":"gp","gaid":"{uid}","brand":"samsung","model":"SM-A025F","system_language":"ar","net":"NETWORK_4G","region":"AE","timezone":"Asia/Baghdad","sp_code":"41820","X-Play-Mode":"1","X-Family-Mode":"0"}}',
                    'x-client-status': "0",
                    'x-tr-signature': final_header,
                    'x-client-token': "1770642922926,35074f554dd1d5738838489ff862d154",
                    'priority': "u=1, i"
                }

                full_url = f"https://{parsed.netloc}{parsed.path}?{sorted_query_encoded}"
                response = requests.get(
                    full_url, headers=headers, verify=False)

                if response.status_code == 200:
                    self.x_user = response.headers.get('x-user')
                    self.auth_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjYxNTE3MzUzMzQ5NTE4NjQ1NjgsImV4cCI6MTc3ODM3MTEzMSwiaWF0IjoxNzcwNTk0ODMxfQ.TcRFEqLQISb3IUPEynOsGM35qBgL4_jwgXqhlZR5KOw"
                    self.root.after(0, lambda: self.auth_status_label.config(
                        bg=self.SUCCESS, fg="white", text="✓ مصادق"))
                    self.log(f"✓ تم المصادقة بنجاح!")
                    self.set_status("✓ تم المصادقة بنجاح")
                else:
                    self.log(f"✗ فشل المصادقة! الحالة: {response.status_code}")
                    self.set_status("✗ فشل المصادقة")
                    self.root.after(0, lambda: self.auth_status_label.config(
                        bg=self.ERROR, fg="white", text="✗ فشل"))

            except Exception as e:
                self.log(f"✗ خطأ في المصادقة: {e}")
                self.set_status("✗ خطأ في المصادقة")
                self.root.after(0, lambda: self.auth_status_label.config(
                    bg=self.ERROR, fg="white", text="✗ خطأ"))

        threading.Thread(target=auth_thread, daemon=True).start()

    def search_content(self):
        """Search for movies or series"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showwarning("تنبيه", "الرجاء إدخال كلمة البحث")
            return

        if not self.x_user:
            messagebox.showwarning("تنبيه", "الرجاء الانتظار حتى اكتمال المصادقة")
            return

        def search_thread():
            try:
                self.set_status("🔍 جاري البحث...")
                self.log(f"\n🔍 جاري البحث عن: {keyword}")

                URL = "https://api6.aoneroom.com/wefeed-mobile-bff/subject-api/search/v2"
                PATH = "/wefeed-mobile-bff/subject-api/search/v2"

                payload_dict = {
                    "page": 1,
                    "perPage": 20,
                    "keyword": keyword
                }
                payload_str = json.dumps(
                    payload_dict, separators=(',', ':'), ensure_ascii=False)
                payload_bytes = payload_str.encode('utf-8')

                method = "POST"
                timestamp = str(int(time.time() * 1000))
                accept_val = "application/json"
                content_type_val = "application/json; charset=utf-8"
                content_length_val = str(len(payload_bytes))
                body_md5 = hashlib.md5(payload_bytes).hexdigest()

                final_header = self.get_auth_headers(
                    method, PATH, timestamp, accept_val, content_type_val, content_length_val, body_md5)

                headers = {
                    'User-Agent': "com.community.oneroom/50020075 (Linux; U; Android 12; ar_AE; SM-A025F; Build/SP1A.210812.016; Cronet/144.0.7509.3)",
                    'Content-Type': content_type_val,
                    'Accept': accept_val,
                    'x-play-mode': "2",
                    'x-family-mode': "0",
                    'x-client-status': "1",
                    'x-tr-signature': final_header,
                    'authorization': self.auth_token,
                    'priority': "u=1, i"
                }

                response = requests.post(
                    URL, data=payload_bytes, headers=headers, verify=False)

                if response.status_code == 200:
                    result = response.json()
                    self.search_results = []

                    def update_ui():
                        self.results_listbox.delete(0, tk.END)
                        try:
                            subjects = result['data']['results'][0]['subjects']
                            for item in subjects:
                                title = item.get('title', 'غير معروف')
                                subject_id = item.get('subjectId', '')
                                content_type = item.get('contentType', '')
                                type_name = "🎬 فيلم" if content_type == 1 else "📺 مسلسم"

                                display_text = f"{title} - {type_name}"
                                self.results_listbox.insert(tk.END, display_text)

                                self.search_results.append({
                                    'title': title,
                                    'subjectId': subject_id,
                                    'contentType': content_type,
                                    'data': item
                                })
                        except (KeyError, IndexError) as e:
                            self.log(f"✗ خطأ في قراءة نتائج البحث: {e}")

                        self.log(f"✓ تم العثور على {len(self.search_results)} نتيجة")
                        self.set_status(f"✓ {len(self.search_results)} نتيجة")

                    self.root.after(0, update_ui)
                else:
                    self.log(f"✗ فشل البحث! الحالة: {response.status_code}")
                    self.set_status("✗ فشل البحث")

            except Exception as e:
                self.log(f"✗ خطأ في البحث: {e}")
                self.set_status("✗ خطأ في البحث")

        threading.Thread(target=search_thread, daemon=True).start()

    def on_result_select(self, event):
        """Handle result selection from listbox"""
        selection = self.results_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.search_results):
                item = self.search_results[index]
                self.selected_subject = item

                title = item['title'][:40] + "..." if len(item['title']) > 40 else item['title']
                type_name = "📺 مسلسم" if item['contentType'] != 1 else "🎬 فيلم"
                self.title_label.config(text=title)
                self.type_label.config(text=type_name)

                self.log(f"\n✓ تم الاختيار: {item['title']}")

                # Load seasons/episodes info for series
                if item['contentType'] != 1:
                    self.load_series_info()
                else:
                    self.clear_episodes_frame()

    def clear_episodes_frame(self):
        """Clear the episodes selection frame"""
        for widget in self.episodes_inner_frame.winfo_children():
            widget.destroy()
        self.episodes_data = []
        self.episode_checkboxes = {}
        self.update_selected_count()

    def load_series_info(self):
        """Load series seasons info"""
        def load_thread():
            try:
                self.set_status("📡 جاري تحميل معلومات المسلسل...")
                self.log("📡 جاري تحميل معلومات المواسم...")

                subject_id = self.selected_subject['subjectId']
                season_data = self.get_season_info(subject_id)

                if season_data and 'data' in season_data:
                    data = season_data['data']
                    seasons = data.get('seasons', [])

                    def update_ui():
                        if seasons:
                            season_list = [f"موسم {s.get('se', s.get('seasonNumber', 1))}" for s in seasons]
                        else:
                            season_list = ["موسم 1"]
                        self.season_combo['values'] = season_list
                        self.season_combo.current(0)

                        if seasons:
                            self.seasons_data = {f"موسم {s.get('se', s.get('seasonNumber', 1))}": s for s in seasons}
                        else:
                            self.seasons_data = {"موسم 1": {}}

                        self.load_season_episodes()
                        self.set_status("✓ تم تحميل معلومات المسلسل")

                    self.root.after(0, update_ui)
                else:
                    self.root.after(0, lambda: self.load_season_episodes())

            except Exception as e:
                self.log(f"✗ خطأ في تحميل معلومات المسلسل: {e}")

        threading.Thread(target=load_thread, daemon=True).start()

    def get_season_info(self, subject_id):
        """Get season information for a series"""
        try:
            URL = f"https://api6.aoneroom.com/wefeed-mobile-bff/subject-api/season-info?subjectId={subject_id}"
            parsed = urlparse(URL)
            path_and_query = parsed.path
            if parsed.query:
                path_and_query += "?" + parsed.query

            method = "GET"
            timestamp = str(int(time.time() * 1000))
            accept_val = "application/json"

            final_header = self.get_auth_headers(
                method, path_and_query, timestamp, accept_val, "", "", "")

            headers = {
                'User-Agent': "com.community.oneroom/50020075 (Linux; U; Android 12; ar_AE; SM-A025F)",
                'Accept': accept_val,
                'x-play-mode': "2",
                'x-family-mode': "0",
                'x-client-status': "1",
                'x-tr-signature': final_header,
                'authorization': self.auth_token,
                'priority': "u=1, i"
            }

            response = requests.get(URL, headers=headers, verify=False)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            self.log(f"خطأ في الحصول على معلومات المواسم: {e}")
        return None

    def load_season_episodes(self):
        """Load episodes for selected season"""
        if not self.selected_subject:
            return

        def load_thread():
            try:
                self.set_status("📡 جاري تحميل الحلقات...")
                self.clear_episodes_frame()

                subject_id = self.selected_subject['subjectId']
                season_name = self.season_var.get()
                season_info = self.seasons_data.get(season_name, {})
                season_num = season_info.get('se', season_info.get('seasonNumber', 1))

                # Get resolution
                resolution_val = self.resolution_var.get()
                if resolution_val == "الافتراضي":
                    resolution = 0
                elif "360p" in resolution_val:
                    resolution = 360
                elif "480p" in resolution_val:
                    resolution = 480
                elif "720p" in resolution_val:
                    resolution = 720
                elif "1080p" in resolution_val:
                    resolution = 1080
                else:
                    resolution = 0

                self.log(f"📡 جاري تحميل حلقات {season_name}...")

                all_episodes = []
                seen_episode_numbers = set()
                ep_from = 1
                batch_size = 20

                while True:
                    ep_to = ep_from + batch_size - 1
                    # Fixed URL with correct parameters
                    URL = f"https://api3.aoneroom.com/wefeed-mobile-bff/subject-api/resource?subjectId={subject_id}&all=0&startPosition={ep_from}&endPosition={ep_to}&pagerMode=0&resolution={resolution}&se={season_num}"

                    parsed = urlparse(URL)
                    params = dict(parse_qsl(parsed.query))
                    sorted_query = urlencode(sorted(params.items()))
                    path_and_query = f"{parsed.path}?{sorted_query}"

                    method = "GET"
                    timestamp = str(int(time.time() * 1000))
                    accept_val = "application/json"

                    final_header = self.get_auth_headers(
                        method, path_and_query, timestamp, accept_val, "", "", "")

                    headers = {
                        'User-Agent': "com.community.oneroom/50020075 (Linux; U; Android 12; ar_AE; SM-A025F)",
                        'Accept': accept_val,
                        'x-play-mode': "2",
                        'x-family-mode': "0",
                        'x-client-status': "1",
                        'x-tr-signature': final_header,
                        'authorization': self.auth_token,
                        'priority': "u=1, i"
                    }

                    response = requests.get(
                        f"https://{parsed.netloc}{path_and_query}", headers=headers, verify=False)

                    if response.status_code == 200:
                        data = response.json()
                        if 'data' in data:
                            data_obj = data['data']
                            episodes = []
                            has_more = False

                            # Handle different response structures
                            if isinstance(data_obj, dict):
                                # Check for common keys
                                if 'list' in data_obj:
                                    episodes = data_obj['list']
                                elif 'episodes' in data_obj:
                                    episodes = data_obj['episodes']
                                elif 'resources' in data_obj:
                                    episodes = data_obj['resources']
                                elif 'data' in data_obj:
                                    # Nested data structure
                                    nested = data_obj['data']
                                    if isinstance(nested, list):
                                        episodes = nested
                                    elif isinstance(nested, dict):
                                        episodes = nested.get('list', nested.get('episodes', nested.get('resources', [])))
                                else:
                                    # Try to get episodes from other possible keys
                                    for key in ['playlist', 'items', 'playlistItems', 'subjects']:
                                        if key in data_obj:
                                            val = data_obj[key]
                                            if isinstance(val, list):
                                                episodes = val
                                                break

                                pager = data_obj.get('pager', {})
                                has_more = pager.get('hasMore', False)
                            elif isinstance(data_obj, list):
                                episodes = data_obj
                                has_more = False

                            if episodes:
                                new_episodes = []
                                for ep in episodes:
                                    if not isinstance(ep, dict):
                                        continue

                                    # Get episode number from various possible fields
                                    ep_num = ep.get('episode') or ep.get('ep') or ep.get('episodeNumber') or ep.get('episode_number')

                                    # If no episode number, use index
                                    if ep_num is None:
                                        ep_num = len(all_episodes) + len(new_episodes) + 1

                                    # Convert to int for comparison
                                    try:
                                        ep_num_int = int(ep_num)
                                    except (ValueError, TypeError):
                                        ep_num_int = len(all_episodes) + len(new_episodes) + 1

                                    if ep_num_int not in seen_episode_numbers:
                                        seen_episode_numbers.add(ep_num_int)
                                        # Ensure episode has the episode field
                                        if 'episode' not in ep:
                                            ep['episode'] = ep_num_int
                                        new_episodes.append(ep)

                                if new_episodes:
                                    all_episodes.extend(new_episodes)
                                    if has_more:
                                        ep_from = ep_to + 1
                                    else:
                                        break
                                else:
                                    break
                            else:
                                if not all_episodes:
                                    self.log(f"  لم يتم العثور على حلقات (هيكل البيانات غير معروف)")
                                    self.log(f"  هيكل الاستجابة: {str(data_obj)[:200]}")
                                break
                        else:
                            if not all_episodes:
                                self.log(f"  لا توجد بيانات في الاستجابة")
                            break
                    else:
                        self.log(f"  فشل الطلب! الحالة: {response.status_code}")
                        break

                    if len(all_episodes) >= 1000:
                        break

                def update_ui():
                    self.episodes_data = all_episodes
                    self.create_episode_checkboxes(all_episodes)
                    self.log(f"✓ تم تحميل {len(all_episodes)} حلقة")
                    self.set_status(f"✓ {len(all_episodes)} حلقة")

                self.root.after(0, update_ui)

            except Exception as e:
                self.log(f"✗ خطأ في تحميل الحلقات: {e}")

        threading.Thread(target=load_thread, daemon=True).start()

    def create_episode_checkboxes(self, episodes):
        """Create enhanced checkbox widgets for episodes"""
        self.episode_checkboxes = {}

        for idx, ep in enumerate(episodes):
            ep_num = ep.get("episode", idx + 1)
            title = ep.get("title", f"حلقة {ep_num}")
            size = int(ep.get("size", 0))
            size_mb = f"{size / (1024*1024):.1f} م.ب" if size else "؟"

            var = tk.BooleanVar(value=False)
            self.episodes_data[idx]["_var"] = var
            self.episodes_data[idx]["_selected"] = False

            # Enhanced row frame with better styling
            row_frame = tk.Frame(self.episodes_inner_frame, bg=self.INPUT_BG, relief="flat", borderwidth=0)
            row_frame.grid(row=idx // 5, column=idx % 5, sticky=tk.W, padx=4, pady=4)

            # Enhanced checkbox
            cb = tk.Checkbutton(
                row_frame,
                variable=var,
                command=self.update_selected_count,
                bg=self.INPUT_BG,
                activebackground=self.ACCENT_LIGHT,
                selectcolor=self.ACCENT,
                fg=self.TEXT,
                activeforeground=self.TEXT
            )
            cb.pack(side=tk.RIGHT, padx=(4, 0))

            label_text = f"{ep_num}"
            label = tk.Label(row_frame, text=label_text, font=("Segoe UI", 9, "bold"), bg=self.INPUT_BG, fg=self.ACCENT)
            label.pack(side=tk.RIGHT, padx=(2, 0))

            size_label = tk.Label(row_frame, text=size_mb, font=("Segoe UI", 8), bg=self.INPUT_BG, fg=self.TEXT_SEC)
            size_label.pack(side=tk.RIGHT, padx=(6, 0))

            self.episode_checkboxes[ep_num] = var

        self.episodes_inner_frame.update_idletasks()
        self.episodes_canvas.configure(scrollregion=self.episodes_canvas.bbox("all"))

    def update_selected_count(self):
        """Update the selected episodes count"""
        count = sum(1 for ep in self.episodes_data if ep.get('_var', tk.BooleanVar()).get())
        self.selected_count_label.config(text=f"{count}")

    def select_all_episodes(self):
        """Select all episodes"""
        for ep in self.episodes_data:
            if '_var' in ep:
                ep['_var'].set(True)
        self.update_selected_count()

    def deselect_all_episodes(self):
        """Deselect all episodes"""
        for ep in self.episodes_data:
            if '_var' in ep:
                ep['_var'].set(False)
        self.update_selected_count()

    def get_selected_links(self):
        """Get download links for selected episodes"""
        if not self.selected_subject:
            messagebox.showwarning("تنبيه", "الرجاء اختيار محتوى أولاً")
            return

        selected_eps = [ep for ep in self.episodes_data if ep.get("_var", tk.BooleanVar()).get()]

        if not selected_eps:
            messagebox.showwarning("تنبيه", "الرجاء تحديد حلقة واحدة على الأقل")
            return

        def get_thread():
            try:
                self.output_text.delete(1.0, tk.END)
                self.download_links = []

                self.log(f"📡 جاري الحصول على روابط {len(selected_eps)} حلقة...")
                self.set_status("📡 جاري الحصول على الروابط...")

                for ep in selected_eps:
                    ep_num = ep.get("episode", "؟")
                    title = ep.get("title", f"حلقة {ep_num}")
                    resource_link = ep.get("resourceLink", "")
                    size = ep.get("size", "غير معروف")

                    self.download_links.append({
                        "episode": ep_num,
                        "title": title,
                        "url": resource_link,
                        "size": size
                    })

                    self.log(f"✓ حلقة {ep_num}: {title}")

                self.set_status(f"✓ {len(self.download_links)} رابط")

            except Exception as e:
                self.log(f"✗ خطأ: {e}")

        threading.Thread(target=get_thread, daemon=True).start()

    def save_urls_to_file(self):
        """Save collected download URLs to a file"""
        if not self.download_links:
            messagebox.showwarning("تنبيه", "لم يتم جمع روابط بعد")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("ملفات نصية", "*.txt"), ("جميع الملفات", "*.*")],
            initialfile=f"{self.selected_subject['title']}_روابط.txt"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# روابط التحميل لـ: {self.selected_subject['title']}\n")
                    f.write(f"# الإجمالي: {len(self.download_links)} حلقات\n\n")
                    for item in self.download_links:
                        f.write(f"# حلقة {item['episode']}: {item['title']}\n")
                        f.write(f"{item['url']}\n\n")
                self.log(f"\n✓ تم حفظ الروابط في: {file_path}")
                messagebox.showinfo("نجاح", f"تم حفظ الروابط في:\n{file_path}")
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل حفظ الملف:\n{e}")

    def browse_folder(self):
        """Browse and select download folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.save_path_var.set(folder)

    def start_batch_download(self):
        """Start batch download of selected episodes"""
        if not self.download_links:
            messagebox.showwarning("تنبيه", "لم يتم جمع روابط بعد")
            return

        save_folder = self.save_path_var.get()
        if not save_folder:
            messagebox.showwarning("تنبيه", "الرجاء تحديد مجلد الحفظ")
            return

        os.makedirs(save_folder, exist_ok=True)

        # Create enhanced download window
        self.download_window = tk.Toplevel(self.root)
        self.download_window.title("نافذة التحميل")
        self.download_window.geometry("650x480")
        self.download_window.transient(self.root)
        self.download_window.grab_set()
        self.download_window.configure(bg=self.BG)

        frame = tk.Frame(self.download_window, bg=self.CARD)
        frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        # Enhanced header
        header_frame = tk.Frame(frame, bg=self.CARD)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(header_frame, text="⬇️", font=("Segoe UI", 20), bg=self.CARD, fg=self.ACCENT).pack(side=tk.RIGHT, padx=(0, 10))
        tk.Label(header_frame, text="جاري التحميل", font=(
            "Segoe UI", 16, "bold"), bg=self.CARD, fg=self.TEXT).pack(side=tk.RIGHT)

        # Enhanced progress section
        progress_frame = tk.Frame(frame, bg=self.INPUT_BG)
        progress_frame.pack(fill=tk.X, pady=(0, 15), ipady=12, ipadx=12)

        # Overall progress
        tk.Label(progress_frame, text="التقدم الكلي:", font=(
            "Segoe UI", 10, "bold"), bg=self.INPUT_BG, fg=self.TEXT_SEC).pack(anchor=tk.W, padx=12, pady=(0, 6))

        progress_bar_frame = tk.Frame(progress_frame, bg=self.INPUT_BG)
        progress_bar_frame.pack(fill=tk.X, padx=12, pady=(0, 8))

        self.overall_progress = ttk.Progressbar(
            progress_bar_frame, length=400, mode='determinate')
        self.overall_progress.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.overall_label = tk.Label(progress_bar_frame, text="0%", font=("Segoe UI", 10, "bold"),
                                      bg=self.ACCENT, fg="white", padx=8, pady=2)
        self.overall_label.pack(side=tk.LEFT, padx=(8, 0))

        # Current file progress
        tk.Label(progress_frame, text="الملف الحالي:", font=(
            "Segoe UI", 10, "bold"), bg=self.INPUT_BG, fg=self.TEXT_SEC).pack(anchor=tk.W, padx=12, pady=(8, 6))

        file_progress_frame = tk.Frame(progress_frame, bg=self.INPUT_BG)
        file_progress_frame.pack(fill=tk.X, padx=12, pady=(0, 0))

        self.file_progress = ttk.Progressbar(
            file_progress_frame, length=400, mode='determinate')
        self.file_progress.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.file_percent_label = tk.Label(file_progress_frame, text="0%", font=("Segoe UI", 9),
                                          bg=self.INPUT_BG, fg=self.TEXT_SEC)
        self.file_percent_label.pack(side=tk.LEFT, padx=(8, 0))

        # Enhanced status labels
        status_frame = tk.Frame(frame, bg=self.CARD)
        status_frame.pack(fill=tk.X, pady=(15, 0))

        self.download_status = tk.Label(
            status_frame, text="● جاري التحضير...", font=("Segoe UI", 11, "bold"),
            bg=self.CARD, fg=self.TEXT_SEC)
        self.download_status.pack(anchor=tk.W, pady=(0, 8))

        self.current_file_label = tk.Label(status_frame, text="", font=("Segoe UI", 10),
                                          bg=self.CARD, fg=self.TEXT_SEC)
        self.current_file_label.pack(anchor=tk.W, pady=(0, 6))

        info_frame = tk.Frame(status_frame, bg=self.CARD)
        info_frame.pack(anchor=tk.W)

        self.speed_label = tk.Label(info_frame, text="", font=("Segoe UI", 9), bg=self.CARD, fg=self.TEXT_SEC)
        self.speed_label.pack(side=tk.RIGHT, padx=(0, 20))

        self.size_label = tk.Label(info_frame, text="", font=("Segoe UI", 9), bg=self.CARD, fg=self.TEXT_SEC)
        self.size_label.pack(side=tk.RIGHT)

        # Enhanced cancel button
        button_frame = tk.Frame(frame, bg=self.CARD)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        tk.Button(button_frame, text="✖ إلغاء التحميل",
                   command=self.cancel_download, bg=self.ERROR, fg="white",
                   font=("Segoe UI", 11, "bold"), padx=25, pady=10, cursor="hand2",
                   relief="flat", borderwidth=0, activebackground=self.ERROR_LIGHT).pack(side=tk.LEFT)

        self.downloading = True
        self.stop_download = False

        threading.Thread(target=self._batch_download_thread,
                         args=(save_folder,), daemon=True).start()

    def cancel_download(self):
        """Cancel current download"""
        self.stop_download = True
        self.download_status.config(text="جاري الإلغاء...")

    def _batch_download_thread(self, save_folder):
        """Thread function for batch download with enhanced progress tracking"""
        total_files = len(self.download_links)
        completed = 0

        for idx, item in enumerate(self.download_links):
            if self.stop_download:
                break

            url = item['url']
            ep_num = item['episode']
            title = item['title'] or f"حلقة_{ep_num}"

            safe_title = "".join(c for c in title if c.isalnum()
                                 or c in (' ', '-', '_')).strip()
            if not safe_title:
                safe_title = f"حلقة_{ep_num}"
            filename = f"{ep_num}_{safe_title}.mp4"
            filepath = os.path.join(save_folder, filename)

            # Update current file info
            self.root.after(0, lambda f=filename: self.current_file_label.config(
                text=f"📄 {f[:50]}..." if len(f) > 50 else f"📄 {f}"))

            # Update overall progress
            overall_percent = int((completed / total_files) * 100) if total_files > 0 else 0
            self.root.after(0, lambda p=overall_percent: self.overall_label.config(text=f"{p}%"))
            self.root.after(0, lambda p=overall_percent: self.overall_progress.config(value=p))

            try:
                self._download_file(url, filepath, idx, total_files)
                completed += 1
            except Exception as e:
                self.root.after(0, lambda err=str(e): self.download_status.config(
                    text=f"✗ فشل: {err}", fg=self.ERROR))

        # Final update
        final_percent = int((completed / total_files) * 100) if total_files > 0 else 0
        self.root.after(0, lambda: self.overall_label.config(text=f"{final_percent}%"))
        self.root.after(0, lambda: self.overall_progress.config(value=100))
        self.root.after(0, lambda c=completed, t=total_files: self.download_status.config(
            text=f"✓ تم: {c}/{t} ملفات", fg=self.SUCCESS))
        self.downloading = False

    def _download_file(self, url, filepath, file_idx, total_files):
        """Download a single file with enhanced progress tracking"""
        response = requests.get(url, stream=True, verify=False, timeout=60)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 1024
        downloaded = 0
        start_time = time.time()

        mode = 'wb'
        if os.path.exists(filepath):
            existing_size = os.path.getsize(filepath)
            if existing_size < total_size:
                mode = 'ab'
                downloaded = existing_size
                headers = {'Range': f'bytes={downloaded}-'}
                response = requests.get(
                    url, headers=headers, stream=True, verify=False, timeout=60)
                total_size += downloaded

        with open(filepath, mode) as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if self.stop_download:
                    break
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        self.root.after(0, lambda p=percent: self.file_progress.config(value=p))
                        self.root.after(0, lambda p=int(percent): self.file_percent_label.config(text=f"{p}%"))

                        elapsed = time.time() - start_time
                        if elapsed > 0:
                            speed_mb = (downloaded / (1024 * 1024)) / elapsed
                            downloaded_mb = downloaded / (1024 * 1024)
                            total_mb = total_size / (1024 * 1024)

                            self.root.after(0, lambda s=speed_mb: self.speed_label.config(
                                text=f"🚀 {s:.2f} م.ب/ثانية"))
                            self.root.after(0, lambda d=downloaded_mb, t=total_mb: self.size_label.config(
                                text=f"📦 {d:.1f} / {t:.1f} م.ب"))

        # Update status after file completes
        self.root.after(0, lambda: self.speed_label.config(text=f"✓ تم [{file_idx + 1}/{total_files}]"))


def main():
    root = tk.Tk()
    app = AsianPlayerDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
