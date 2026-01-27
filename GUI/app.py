import sys
from PyQt6.QtWidgets import QApplication
from MainWindow import MainWindow
# import qdarktheme


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarktheme.load_stylesheet())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
