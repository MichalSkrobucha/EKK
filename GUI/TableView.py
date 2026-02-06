import sys
import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from style import COLORS, STYLESHEET


class TableView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.row_keys = [
            "Alice bits",
            "Alice bases",
            "Bob bases",
            "Bob bits",
            "Bob hits",
            "Key bits",
            "Eve bases",
            "Eve bits"
        ]

        self.row_labels = [
            "Alice: Bit", "Alice: Base",
            "Bob: Base", "Bob: Bit", "Bob: Match",
            "Raw Key",
            "Eve: Base", "Eve: Bit",
        ]

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.result_table = QTableWidget()
        self.result_table.setRowCount(len(self.row_keys))
        self.result_table.setColumnCount(0)
        self.result_table.setStyleSheet(STYLESHEET)

        self.result_table.setVerticalHeaderLabels(self.row_labels)
        self.result_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.result_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)

        self.result_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        v_header = self.result_table.verticalHeader()
        v_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        v_header.setDefaultSectionSize(50)

        v_header.setSectionsClickable(True)
        v_header.sectionClicked.connect(self.result_table.selectRow)

        h_header = self.result_table.horizontalHeader()
        h_header.setDefaultSectionSize(40)

        self.result_table.setSortingEnabled(False)

        h_header.setSectionsClickable(True)
        h_header.sectionClicked.connect(self.result_table.selectColumn)

        layout.addWidget(self.result_table)

    def update_table(self, df):
        if df is None or df.empty:
            self.result_table.setColumnCount(0)
            return

        num_steps = df.shape[0]

        if self.result_table.columnCount() != num_steps:
            self.result_table.setColumnCount(num_steps)

        labels = [str(i) for i in range(num_steps)]
        self.result_table.setHorizontalHeaderLabels(labels)

        for row_idx, key in enumerate(self.row_keys):
            if key not in df.columns:
                continue

            series = df[key]
            for col_idx, value in enumerate(series):
                if pd.isna(value):
                    text_val = ""
                else:
                    text_val = str(value)

                existing_item = self.result_table.item(row_idx, col_idx)

                if existing_item:
                    if existing_item.text() != text_val:
                        existing_item.setText(text_val)
                        self._style_item(existing_item, key, text_val)
                else:
                    item = QTableWidgetItem(text_val)
                    item.setTextAlignment(Qt.AlignCenter)
                    self._style_item(item, key, text_val)
                    self.result_table.setItem(row_idx, col_idx, item)

        if num_steps > 0:
            last_col = num_steps - 1
            self.result_table.scrollToItem(self.result_table.item(0, num_steps - 1))
            self.result_table.scrollToItem(self.result_table.item(0, last_col))
            self.result_table.setCurrentCell(0, last_col)
            self.result_table.selectColumn(last_col)

    def _style_item(self, item, key, text_val):
        """Metoda pomocnicza do kolorowania"""
        if key == "Bob hits":
            if text_val == "✔":
                item.setForeground(QColor(COLORS['success']))
            elif text_val == "X":
                item.setForeground(QColor(COLORS['error']))
