from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem 

class CustomTable(QTableWidget):
    def __init__(self,table_headers:list,table_items:list=None,parent=None):
        super().__init__(0,len(table_headers),parent)
        self.setHorizontalHeaderLabels(table_headers)
        self.horizontalHeader().setDefaultSectionSize(150)
        self.horizontalHeader().setStretchLastSection(True)

        for row_idx,table_item in enumerate(table_items):
            self.insertRow(row_idx)
            for col_idx,cell_item in enumerate(table_item):
                self.setItem(row_idx,col_idx, QTableWidgetItem(cell_item))