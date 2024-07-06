import os
from pathlib import Path
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMessageBox

bundle_dir = Path(__file__).parent.parent

# Custom Message Box implementation
class MessageBox(QMessageBox):
    def __init__(self, text:str,mode:str="information", information:str=None, parent=None):
        super().__init__(parent)
        if mode=="critical":
            self.setIcon(QMessageBox.Critical)
        elif mode=="warning":
            self.setIcon(QMessageBox.Warning)
        elif mode=="question":
            self.setIcon(QMessageBox.Question)
        else:
            self.setIcon(QMessageBox.Information)
        self.setWindowTitle("Notification")
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(bundle_dir, 'assets/images/arnergy-icon.png'))))
        self.setText(text)
        self.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
        if information:
            self.setInformativeText(information)