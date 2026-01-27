import sys
from PyQt6.QtWidgets import QApplication
from MainWindow import MainWindow

try:
    import qdarktheme
    QDARKTHEME = True
except ImportError:
    QDARKTHEME = False
    print("⚠ Ostrzeżenie: Brak biblioteki 'qdarktheme'. Brak trybu nocnego.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if QDARKTHEME:
        app.setStyleSheet(qdarktheme.load_stylesheet())
    window = MainWindow(dark_theme=True)
    window.show()
    sys.exit(app.exec())
