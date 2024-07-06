import os
import json
from pathlib import Path
from PyQt5 import QtGui,QtCore
from types import FunctionType
from .table import CustomTable
from .form import FormField
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QComboBox,
    QCheckBox,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QPushButton,
    QLabel
)

bundle_dir = Path(__file__).parent.parent
config = json.load(open(os.path.join(bundle_dir,'config.json'), 'r'))
default_settings = {'SIM1':0,'SIM2':2,'SYSTEM_TYPE':0}
saved_settings = QtCore.QSettings('Main', 'settings')
settings = json.loads(saved_settings.value('savedSettings', None)) if saved_settings.value('savedSettings') else default_settings

# Implementation of the Custom class for Settings dialog
class SettingsDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setMinimumWidth(500)
        self.setWindowTitle("Settings")
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(bundle_dir,'assets/images/arnergy-icon.png'))))
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(lambda: self.close())
        self.button_box.rejected.connect(lambda : self.close())
        self.button_box.setStyleSheet(
            'background-color: orange;'+
            'color: #fff;'
        )

        self.set_system_type = QComboBox()
        self.set_system_type.addItems(config["SYSTEM_TYPES"])
        self.set_system_type.setCurrentIndex(settings["SYSTEM_TYPE"])
        self.set_primary_sim = QComboBox()
        self.set_primary_sim.addItems(list(config["NETWORKS"].keys()))
        self.set_primary_sim.setCurrentIndex(settings["SIM1"])
        self.set_secondary_sim = QComboBox()
        self.set_secondary_sim.addItems(list(config["NETWORKS"].keys()))
        self.set_secondary_sim.setCurrentIndex(settings["SIM2"])
        self.settings_form = QFormLayout()
        self.settings_form.addRow('Set Default SYSTEM TYPE: -', self.set_system_type)
        self.settings_form.addRow('Set Default Primary SIM: -', self.set_primary_sim)
        self.settings_form.addRow('Set Default Secondary SIM: -', self.set_secondary_sim)

        # verbose1 = QCheckBox('1', self)
        # verbose2 = QCheckBox('2', self)
        # verbose_hbox = QHBoxLayout()
        # verbose_hbox.addWidget(verbose1)
        # verbose_hbox.addWidget(verbose2)
        # self.settings_form.addRow('Select Verbose Level: -', verbose_hbox)
        self.new_network_button = QPushButton(self)
        self.new_network_button.setText('Add New Network')
        self.new_network_button.setMaximumWidth(100)
        self.new_network_button.clicked.connect(lambda: AddNewNetworkDialog().exec_())
        self.apn_table = CustomTable(table_headers=["Network","APN"], table_items=list(map(list, config["NETWORKS"].items()))) 

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.settings_form)
        self.layout.addWidget(self.new_network_button)
        self.layout.addWidget(self.apn_table)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

class AddNewNetworkDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setMinimumWidth(300)
        self.setWindowTitle("Add New Network")
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(bundle_dir,'assets/images/arnergy-icon.png'))))
        self.layout = QVBoxLayout()
        self.network_name_input = FormField("Network Name: ", "Enter Network Name i.e. MTN")
        self.network_apn_input = FormField("Network APN: ", "Enter Network APN")
        self.submit_button = QPushButton(self)
        self.submit_button.setText('Enter 🡺')
        self.submit_button.setStyleSheet(
            'background: blue;'+
            'height: 24px;'+
            'font-size: 14px;'+
            'color: #fff;'
        )
        self.submit_button.clicked.connect(self.submit_handler)
        self.layout.addLayout(self.network_name_input.layout)
        self.layout.addLayout(self.network_apn_input.layout)
        self.layout.addWidget(self.submit_button)
        self.setLayout(self.layout)

    def submit_handler(self):
        new_network_name = self.network_name_input.input.text()
        new_network_apn = self.network_apn_input.input.text()
        #print(new_network_name,new_network_apn)
        config["NETWORKS"][new_network_name] = new_network_apn 
        #Save the newly added config
        json.dump(config, open(os.path.join(bundle_dir,'config.json'), 'w'),indent=4)
        self.close()