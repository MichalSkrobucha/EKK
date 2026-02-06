# --- KONFIGURACJA KOLORÓW ---
COLORS = {
    "bg_dark": "#1e1e2e",  # Główne tło (Bardzo ciemny fiolet/czerń)
    "bg_panel": "#282a36",  # Tło paneli
    "bg_selected": "#44475a",  # Zaznaczenie

    "text": "#f8f8f2",  # Biały tekst

    "accent": "#bd93f9",  # Fioletowy (Przyciski, Aktywne Tabs)
    "highlight": "#ff79c6",  # Różowy (Hover)
    "secondary": "#6272a4",  # Szaro-niebieski (Ramki)

    "button_text": "#282a36",  # Ciemny tekst na przycisku
    "icon_color": "#f8f8f2",
    "icon_active": "#bd93f9",
    "bg_table": "#282a36",
    "gridline": "#44475a",

    "success": "#50fa7b",  # Jasny zielony
    "error": "#ff5555"  # Czerwony
}

# --- KONFIGURACJA KOLORÓW (MID-DARK / SLATE / GRAPHITE) ---
# To jest ten Twój "szaro-niebieski/grafitowy 50%+"
COLORS_LIGHT = {
    "bg_dark": "#3b4252",  # Baza: Grafitowy łupek (Nordic Grey)
    "bg_panel": "#434c5e",  # Panel: Nieco jaśniejszy grafit
    "bg_selected": "#4c566a",  # Zaznaczenie: Jasny grafit

    "text": "#eceff4",  # Złamana biel (nie razi w oczy na graficie)

    # TWOJE KOLORY:
    "accent": "#bd93f9",  # Fioletowy (taki sam jak w głównym)
    "highlight": "#ffb86c",  # Pomarańczowy (zamiast różu)
    "secondary": "#5e81ac",  # Stonowany niebieski (do ramek)

    "button_text": "#2e3440",  # Ciemny tekst na jasnych przyciskach
    "icon_color": "#d8dee9",  # Jasnoszare ikony
    "icon_active": "#bd93f9",  # Fioletowe aktywne
    "bg_table": "#434c5e",  # Tło tabeli
    "gridline": "#4c566a",  # Linie siatki

    "success": "#a3be8c",  # Stonowany zielony
    "error": "#bf616a"  # Stonowany czerwony
}

# --- ARKUSZ STYLÓW 1 (Dla COLORS - Dracula) ---
STYLESHEET = f"""
QMainWindow {{
    background-color: {COLORS['bg_dark']};
}}

QWidget {{
    color: {COLORS['text']};
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}}

/* ZAKŁADKI PIONOWE */
QTabWidget::pane {{ border: none; }}

QTabBar::tab:left {{
    background: {COLORS['bg_panel']};
    color: {COLORS['accent']};
    padding: 15px 10px;
    margin-bottom: 2px;
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
    min-width: 80px;
    font-weight: bold;
    font-size: 14px;
}}

QTabBar::tab:left:selected {{
    background: {COLORS['bg_selected']};
    color: {COLORS['highlight']};
    border-right: 3px solid {COLORS['highlight']};
}}

/* ZAKŁADKI POZIOME */
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

/* ELEMENTY FORMULARZY */
QTextEdit, QPlainTextEdit, QLineEdit {{
    background-color: {COLORS['bg_panel']}; 
    color: {COLORS['text']};
    border: 1px solid {COLORS['bg_selected']};
    border-radius: 3px;
    padding: 4px;
}}

/* TABELE (Podstawowe style dla Dracula) */
QHeaderView::section {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['text']};
    padding: 4px;
    border: 1px solid {COLORS['bg_selected']};
}}

QTableWidget {{
    gridline-color: {COLORS['gridline']};
}}

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

QPushButton {{
    background-color: {COLORS['accent']};
    color: {COLORS['button_text']};
    border-radius: 3px;
    padding: 6px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {COLORS['highlight']};
}}

QCheckBox {{ spacing: 8px; }}
"""

# --- ARKUSZ DLA PRZYCISKÓW MEDIALNYCH ---
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

# --- ARKUSZ STYLÓW 2 (Dla COLORS_LIGHT - Slate/Graphite) ---
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
    color: {COLORS_LIGHT['accent']}; /* Fioletowy */
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
    color: {COLORS_LIGHT['highlight']}; /* Pomarańczowy */
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

/* --- POLA TEKSTOWE --- */
QTextEdit, QPlainTextEdit, QLineEdit {{
    background-color: {COLORS_LIGHT['bg_panel']}; 
    color: {COLORS_LIGHT['text']};
    border: 1px solid {COLORS_LIGHT['bg_selected']};
    border-radius: 3px;
    padding: 4px;
}}

QLineEdit:focus, QTextEdit:focus {{
    border: 1px solid {COLORS_LIGHT['accent']};
}}

/* --- TABELE (Wersja XL - Zwiększona czytelność) --- */
QTableWidget, QTableView {{
    background-color: {COLORS_LIGHT['bg_table']};
    gridline-color: {COLORS_LIGHT['gridline']};
    color: {COLORS_LIGHT['text']};
    border: none;

    /* GŁÓWNA CZCIONKA TABELI */
    font-size: 16px;
    font-weight: 600;
}}

/* Odstępy wewnątrz komórek */
QTableWidget::item {{
    padding: 10px;
}}

/* Nagłówki po lewej (Wiersze) */
QHeaderView::section:vertical {{
    background-color: {COLORS_LIGHT['bg_selected']};
    color: {COLORS_LIGHT['text']};
    padding: 8px 15px;
    border: 1px solid {COLORS_LIGHT['gridline']};
    font-weight: bold;
    font-size: 14px;
}}

/* Nagłówki na górze (Kroki) */
QHeaderView::section:horizontal {{
    background-color: {COLORS_LIGHT['bg_panel']};
    color: {COLORS_LIGHT['text']};
    border: 1px solid {COLORS_LIGHT['gridline']};
    font-size: 12px;
}}

QTableCornerButton::section {{
    background-color: {COLORS_LIGHT['bg_dark']};
    border: 1px solid {COLORS_LIGHT['bg_selected']};
}}

QTableWidget::item:selected {{
    background-color: {COLORS_LIGHT['highlight']}; /* Pomarańczowy */
    color: {COLORS_LIGHT['bg_dark']}; /* Ciemny tekst na jasnym tle */
}}

/* --- PRZYCISKI --- */
QPushButton {{
    background-color: {COLORS_LIGHT['accent']}; /* Fioletowy */
    color: {COLORS_LIGHT['button_text']};
    border-radius: 3px;
    padding: 6px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {COLORS_LIGHT['highlight']}; /* Pomarańczowy */
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
    image: none;
}}
"""