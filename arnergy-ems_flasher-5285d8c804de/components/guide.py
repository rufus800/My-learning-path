import os
import codecs
from PyQt5 import QtGui
from pathlib import Path
from PyQt5.QtWidgets import QDialog,QPlainTextEdit,QVBoxLayout

bundle_dir = Path(__file__).parent.parent
guide_file = codecs.open(os.path.join(bundle_dir, 'guide.html'), 'r', 'utf-8')
# Implementation of the Guide dialog
class GuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(500)
        self.setMinimumWidth(500)
        self.setWindowTitle("Guide (How to use EMS Flasher Tool)")
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(bundle_dir,'assets/images/arnergy-icon.png'))))
        self.textbox = QPlainTextEdit()
        self.textbox.appendHtml(guide_file.read())
        self.textbox.setReadOnly(True)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.textbox)
        self.setLayout(self.layout)