import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from MainWindow import MainWindow
import qdarktheme
# import QKD_Algorithms as QKD
#
# class AppManager():
#     _instance = None
#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#             cls._instance._app_setup()
#         return cls._instance
#
#     def _app_setup(self):
#         self.bb84_sim = QKD.BB84.SimManager()
#         self.sarg_sim = QKD.SARG04.SimManager()
#         self.e91_sim = QKD.E91.SimManager()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
