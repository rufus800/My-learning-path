import os 
from PyQt5 import QtCore
from PyQt5.QtWidgets import QProgressBar

# Custom Progress Bar implementation
class ProgressBar(QProgressBar):
    def __init__(self, parent=None, initial_value=0):
        super().__init__(parent)
        self.setStyleSheet(
            "QProgressBar::chunk "
            "{"
            "background-color: qlineargradient(spread:pad, x1:0.6, y1:0.5, x2:1, y2:1, stop:0  #3bc860, stop:1 rgba(255, 255, 255, 255));;"+
            "text-align: center;"
            "}"
        )
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setValue(initial_value)
    
    @classmethod
    def set_value(self,value:int)->None:
        """
            Description: To set the value of the progress bar programmatically 
            Args: 
                value (int) : Value between 0 and 100 to indicate progress
        """
        self.setValue(value)