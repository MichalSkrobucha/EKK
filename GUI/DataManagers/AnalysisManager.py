import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal


class AnalysisManager(QObject):
    sig_data_updated = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.eve_results = pd.DataFrame()
        self.heatmap_results = pd.DataFrame()

    def set_eve_data(self, df):
        self.eve_results = df
        self.sig_data_updated.emit(df)

    def set_heatmap_data(self, df):
        self.heatmap_results = df
        self.sig_data_updated.emit(df)

    def get_eve_data(self):
        return self.eve_results