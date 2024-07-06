import os  
from types import FunctionType
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget,QComboBox,QLabel,QVBoxLayout,QLineEdit

# Custom Select Box implementation
class SelectBox(QWidget):
    def __init__(self, label:str, options:list, select_handler:FunctionType, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.label = QLabel(label)
        self.label.setMaximumHeight(24)
        self.label.setStyleSheet('font-weight: bold;')
        self.combo_box = QComboBox()
        self.combo_box.addItems(options)
        self.combo_box.setStyleSheet(
            'height: 24px;'
        )
        self.combo_box.activated.connect(select_handler)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combo_box)
        #self.layout.setContentsMargins(25,25,25,25)

# Custom form input 
class FormField(QWidget):
    def __init__(self, label:str,placeholder:str,max_height:int=30,parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.label = QLabel(f'<b>{label}</b>')
        self.input = QLineEdit()
        self.input.setAlignment(QtCore.Qt.AlignLeft)
        self.input.setPlaceholderText(placeholder)
        self.input.setMaximumHeight(max_height)
        self.input.setStyleSheet(
            f'height: {max_height}px;'
        )
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input)


