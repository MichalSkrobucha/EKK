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

QTextEdit {{
    background-color: {COLORS['bg_panel']};
    border: 1px solid {COLORS['bg_selected']};
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
