# --- KONFIGURACJA KOLORÓW ---
COLORS = {
    "bg_dark": "#1e1e2e",  # Główne tło okna
    "bg_panel": "#282a36",  # Tło paneli, inputów, nieaktywnych zakładek
    "bg_selected": "#44475a",  # Tło zaznaczonych elementów

    "text": "#f8f8f2",  # Główny kolor tekstu

    "accent": "#bd93f9",  # Fioletowy (Tekst zakładek, Przyciski)
    "highlight": "#ff79c6",  # Różowy (Hover, Aktywne elementy)
    "secondary": "#6272a4",  # Szaro-niebieski (Obramowania GroupBox)

    "button_text": "#282a36",  # Ciemny tekst na jasnym przycisku
    "icon_color": "#f8f8f2",
    "icon_active": "#bd93f9",
    "bg_table": "#282a36",
    "gridline": "#44475a"
}

# --- KONFIGURACJA KOLORÓW (MID-DARK / SLATE) ---
COLORS_LIGHT = {
    "bg_dark": "#3b4252",
    "bg_panel": "#434c5e",
    "bg_selected": "#4c566a",

    "text": "#f8f8f2",

    "accent": "#bd93f9",
    "highlight": "#ffb86c",
    "secondary": "#5e81ac",

    "button_text": "#282a36",
    "icon_color": "#d8dee9",
    "icon_active": "#bd93f9",
    "bg_table": "#434c5e",
    "gridline": "#4c566a"
}

# ARKUSZ STYLÓW
# Uwaga: W f-stringu podwójne klamry {{ }} oznaczają styl CSS,
# a pojedyncze { } wstawiają zmienną z Pythona.

STYLESHEET = f"""
/* GŁÓWNE USTAWIENIA */
QMainWindow {{
    background-color: {COLORS['bg_dark']};
}}

QWidget {{
    color: {COLORS['text']};
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}}

/* PIONOWE ZAKŁADKI (Lewy pasek) */
QTabWidget::pane {{
    border: none;
}}

/* Zakładki, gdy są ustawione po lewej stronie */
QTabBar::tab:left {{
    background: {COLORS['bg_panel']};
    color: {COLORS['accent']};
    padding: 15px 10px;
    margin-bottom: 2px;
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
    min-width: 80px;
    font-weight: bold;
    font-size: 20px;
}}

QTabBar::tab:left:selected {{
    background: {COLORS['bg_selected']};
    color: {COLORS['highlight']};
    border-right: 3px solid {COLORS['highlight']};
}}

/* POZIOME ZAKŁADKI (Górny pasek) */
QTabBar::tab:top {{
    background: {COLORS['bg_selected']};
    color: {COLORS['text']};
    padding: 8px 20px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}

QTabBar::tab:top:selected {{
    background: {COLORS['secondary']};
    font-weight: bold;
}}

/* ELEMENTY WEWNĘTRZNE */
QGroupBox {{
    border: 1px solid {COLORS['secondary']};
    border-radius: 5px;
    margin-top: 20px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}}

QTextEdit, QPlainTextEdit, QLineEdit {{
    background-color: {COLORS['bg_panel']}; 
    color: {COLORS['text']};
    border: 1px solid {COLORS['bg_selected']};
    border-radius: 3px;
    padding: 4px;
}}

QPushButton {{
    background-color: {COLORS['accent']};
    color: {COLORS['button_text']};
    border-radius: 3px;
    padding: 5px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {COLORS['highlight']};
}}

/* Wyrównanie Checkboxa w formularzach */
QCheckBox {{
    spacing: 8px;
    margin-bottom: 2px;
}}
"""

MEDIA_BUTTON_SHEET = f"""
QPushButton {{
    background-color: transparent;
    border: none;
    border-radius: 4px;
    padding: 5px;
}}
QPushButton:hover {{
    background-color: {COLORS['bg_selected']};
}}
QPushButton:pressed {{
    background-color: {COLORS['secondary']};
}}
"""

# ARKUSZ STYLÓW (LIGHT)
STYLESHEET_LIGHT = f"""
/* --- GŁÓWNE --- */
QMainWindow {{
    background-color: {COLORS_LIGHT['bg_dark']};
}}

QWidget {{
    color: {COLORS_LIGHT['text']};
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}}

/* --- ZAKŁADKI (Lewy pasek) --- */
QTabWidget::pane {{ border: none; }}

QTabBar::tab:left {{
    background: {COLORS_LIGHT['bg_panel']};
    color: {COLORS_LIGHT['text']};
    padding: 15px 10px;
    margin-bottom: 2px;
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
    min-width: 80px;
    font-weight: bold;
}}

QTabBar::tab:left:selected {{
    background: {COLORS_LIGHT['bg_selected']};
    color: {COLORS_LIGHT['accent']};
    border-right: 3px solid {COLORS_LIGHT['accent']};
}}

/* --- ZAKŁADKI (Górny pasek) --- */
QTabBar::tab:top {{
    background: {COLORS_LIGHT['bg_panel']};
    color: {COLORS_LIGHT['text']};
    padding: 8px 20px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}

QTabBar::tab:top:selected {{
    background: {COLORS_LIGHT['bg_selected']};
    color: {COLORS_LIGHT['highlight']};
    font-weight: bold;
    border-bottom: 2px solid {COLORS_LIGHT['highlight']};
}}

/* --- GROUPBOX --- */
QGroupBox {{
    border: 1px solid {COLORS_LIGHT['bg_selected']};
    border-radius: 5px;
    margin-top: 20px;
    font-weight: bold;
    background-color: {COLORS_LIGHT['bg_dark']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: {COLORS_LIGHT['secondary']};
}}

/* --- POLA TEKSTOWE (Inputy) --- */
QTextEdit, QPlainTextEdit, QLineEdit {{
    background-color: {COLORS_LIGHT['bg_panel']}; 
    color: {COLORS_LIGHT['text']};
    border: 1px solid {COLORS_LIGHT['bg_selected']};
    border-radius: 3px;
    padding: 4px;
}}

/* Aktywne pole tekstowe (Focus) */
QLineEdit:focus, QTextEdit:focus {{
    border: 1px solid {COLORS_LIGHT['accent']};
}}

/* --- TABELE (To naprawia nagłówki) --- */
QTableWidget, QTableView {{
    background-color: {COLORS_LIGHT['bg_panel']};
    gridline-color: {COLORS_LIGHT['gridline']};
    color: {COLORS_LIGHT['text']};
    border: 1px solid {COLORS_LIGHT['bg_selected']};
}}

/* Nagłówki kolumn i wierszy */
QHeaderView::section {{
    background-color: {COLORS_LIGHT['bg_dark']}; /* Ciemniejsze tło nagłówka */
    color: {COLORS_LIGHT['text']};              /* Jasny tekst */
    padding: 5px;
    border: 1px solid {COLORS_LIGHT['bg_selected']};
    font-weight: bold;
}}

/* Pusty róg tabeli (góra-lewo) */
QTableCornerButton::section {{
    background-color: {COLORS_LIGHT['bg_dark']};
    border: 1px solid {COLORS_LIGHT['bg_selected']};
}}

/* Zaznaczenie w tabeli */
QTableWidget::item:selected {{
    background-color: {COLORS_LIGHT['bg_selected']};
    color: {COLORS_LIGHT['highlight']};
}}

/* --- PRZYCISKI --- */
QPushButton {{
    background-color: {COLORS_LIGHT['accent']};
    color: {COLORS_LIGHT['button_text']};
    border-radius: 3px;
    padding: 6px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {COLORS_LIGHT['highlight']};
    color: {COLORS_LIGHT['button_text']};
}}

/* --- CHECKBOX / SPINBOX --- */
QDoubleSpinBox, QSpinBox {{
    background-color: {COLORS_LIGHT['bg_panel']};
    color: {COLORS_LIGHT['text']};
    border: 1px solid {COLORS_LIGHT['bg_selected']};
    padding: 3px;
    border-radius: 3px;
}}

QCheckBox {{
    spacing: 8px;
    color: {COLORS_LIGHT['text']};
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    background: {COLORS_LIGHT['bg_panel']};
    border: 1px solid {COLORS_LIGHT['secondary']};
    border-radius: 3px;
}}

QCheckBox::indicator:checked {{
    background: {COLORS_LIGHT['accent']};
    border: 1px solid {COLORS_LIGHT['accent']};
    image: none; /* Domyślny systemowy ptaszek może być czarny, więc to czyści */
}}
"""
