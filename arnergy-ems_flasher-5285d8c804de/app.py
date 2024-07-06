import sys
import sqlite3
import time
import json
import serial 
import serial.tools.list_ports
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThreadPool, pyqtSlot, pyqtSignal
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog,
    QPlainTextEdit,
    QToolBar,
    QAction,
    QLabel,
    QComboBox,
    QInputDialog,
    QApplication,
    QHBoxLayout,
    QWidget,
    QTableWidget,
    QMainWindow,
    QPushButton,
    QDesktopWidget,
    QVBoxLayout,
    QGridLayout,
    QLineEdit,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView
)   

from utils import *
from components.guide import GuideDialog
from components.form import SelectBox,FormField
from components.messagebox import MessageBox
from components.progressbar import ProgressBar
from components.settings import SettingsDialog

bundle_dir = Path(__file__).parent
print('Starting....')
config = json.load(open(os.path.join(bundle_dir,'config.json'), 'r'))
saved_settings = {'SIM1':0,'SIM2':2,'SYSTEM_TYPE':0}

# Main Window
class EMSFlasherApp(QMainWindow):
    def __init__(self, width:int=1024, height:int=600, parent=None):
        super(EMSFlasherApp, self).__init__(parent)
        global saved_settings
        sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        self.width, self.height = sizeObject.width() - 500, sizeObject.height() - 300
        self.selected_rows= set()
        self.settings = QtCore.QSettings('Main', 'settings')
        saved_settings = json.loads(self.settings.value('savedSettings', None)) if self.settings.value('savedSettings') else saved_settings
        self.load_ui()
        self.show()


    def load_ui(self):
        """ 
            Description: Loads the main user interface 
        """
        self.setWindowTitle("Arnergy EMS Flasher (BETA V0.1.2)")
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(bundle_dir,'assets/images/arnergy-icon.png'))))
        self.resize(self.width, self.height)

        ## Toolbar 
        self.actions_toolbar = QToolBar('actions', self)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.actions_toolbar)
        self.actions_toolbar.setIconSize(QtCore.QSize(48,48))
        self.actions_toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        # Toolbar actions (with Icons)
        firmware_icon = QtGui.QIcon(QtGui.QPixmap(os.path.join(bundle_dir,'assets/icons/firmware.svg')))
        self.action_flash_firmware = QAction("Flash Firmware",self, triggered=lambda : print("Program Firmware"))
        self.action_flash_firmware.setIcon(firmware_icon)
        self.action_flash_firmware.setIconText("Flash Firmware")

        ota_icon = QtGui.QIcon(QtGui.QPixmap(os.path.join(bundle_dir,'assets/icons/ota.svg')))
        self.action_ota = QAction(self)
        self.action_ota.setIcon(ota_icon)
        self.action_ota.setIconText("OTA")

        settings_icon = QtGui.QIcon(QtGui.QPixmap(os.path.join(bundle_dir,'assets/icons/settings.svg')))
        self.action_settings = QAction(self, triggered=lambda: Settings().exec())
        self.action_settings.setIcon(settings_icon)
        self.action_settings.setIconText("Settings")

        guide_icon = QtGui.QIcon(QtGui.QPixmap(os.path.join(bundle_dir,'assets/icons/guide.svg')))
        self.action_guide = QAction(self, triggered=lambda: GuideDialog().exec())
        self.action_guide.setIcon(guide_icon)
        self.action_guide.setIconText("Guide")


        exit_icon = QtGui.QIcon(QtGui.QPixmap(os.path.join(bundle_dir,'assets/icons/exit.svg')))
        self.action_exit = QAction("Exit",self, triggered=lambda x: self.close())
        self.action_exit.setIcon(exit_icon)
        self.action_exit.setIconText("Exit")

        self.action_flash_firmware.setEnabled(False)
        self.action_ota.setEnabled(False)

        # Adding actions for the toolbar buttons, triggered when the buttons are clicked
        self.actions_toolbar.addAction(self.action_flash_firmware)
        self.actions_toolbar.addAction(self.action_ota)
        self.actions_toolbar.addAction(self.action_settings)
        self.actions_toolbar.addAction(self.action_guide)
        self.actions_toolbar.addAction(self.action_exit)
        self.actions_toolbar.setStyleSheet(
            'background-color: #fff;'
        )

        self.device_setup = DeviceSetup(self)
        self.device_setup.setContentsMargins(20,20,20,20)
        self.setCentralWidget(self.device_setup)
        self.center()

    def center(self):
        """ 
            Description: Automatically center the window 
        """
        qRectangle = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        qRectangle.moveCenter(center)
        self.move(qRectangle.topLeft())
    
    def closeEvent(self, a0: QtGui.QCloseEvent)->None:
        """ Event when the GUI is closed """
        global saved_settings
        print(saved_settings)
        self.settings.setValue("savedSettings", json.dumps(saved_settings))
        print("Application Closed.")
        return super().closeEvent(a0)

# The Device setup widget (default main widget)
class DeviceSetup(QWidget):
    # Pyqt signals 
    exceptionSignal = pyqtSignal(str)
    setupComPortSignal = pyqtSignal(str)
    sendCustomerIdSignal = pyqtSignal(str)
    sendBoardIdSignal = pyqtSignal(str)
    sendClientCertificateSignal = pyqtSignal()
    sendPrivateKeySignal = pyqtSignal()
    sendEnergyDataSignal = pyqtSignal()
    sendNetwork1ConfigurationSignal = pyqtSignal()
    sendNetwork2ConfigurationSignal = pyqtSignal()
    sendSystemTypeConfigurationSignal = pyqtSignal()
    completedSetupSignal = pyqtSignal()
    def __init__(self, parent=None):
        super(DeviceSetup, self).__init__(parent)
        self.main = QGridLayout()
        self.network_names = list(config["NETWORKS"].keys())
        self.sim1 = self.network_names[saved_settings["SIM1"]]
        self.sim2 = self.network_names[saved_settings["SIM2"]]
        self.system_type = config["SYSTEM_TYPES"][saved_settings["SYSTEM_TYPE"]]

        # Establish connection to the SQLite database
        self.conn = sqlite3.connect('UID.db')
        self.c = self.conn.cursor()
        
        # Create a table in the database to store the sent and received strings
        self.c.execute('''CREATE TABLE IF NOT EXISTS id_batch
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_Snumber TEXT NOT NULL DEFAULT '')''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS id_batch_serial_number
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                serial_number TEXT NOT NULL,
                batch_Snumber TEXT NOT NULL DEFAULT '')''')
        self.conn.commit()


        # For specifying the network format (SIM or APN)
        self.network1_format = 'sim'
        self.network2_format = 'sim'
        self.device = None  ## Connected device on COM port 
        self.sim1_select = SelectBox('Activate SIM1:',[*self.network_names,'Other'], self.select_sim1_handler)
        self.sim1_select.combo_box.setCurrentIndex(self.network_names.index(self.sim1))
        self.sim2_select = SelectBox('Activate SIM2:',[*self.network_names,'Other'], self.select_sim2_handler)
        self.sim2_select.combo_box.setCurrentIndex(self.network_names.index(self.sim2))
        self.system_type_select = SelectBox('Select System Type:',config["SYSTEM_TYPES"], self.select_system_type_handler)
        self.system_type_select.combo_box.setCurrentIndex(config["SYSTEM_TYPES"].index(self.system_type))
        self.customer_id = QLineEdit()
        self.customer_id.setValidator(QtGui.QIntValidator())
        self.customer_id.setMaxLength(10)
        self.customer_id.setAlignment(QtCore.Qt.AlignLeft)
        #self.customer_id.setContentsMargins(20,20,20,20)
        self.customer_id.setPlaceholderText('Enter Customer ID i.e. 416813')
        self.customer_id.setMaximumHeight(40)
        self.customer_id.setStyleSheet(
            'height: 40px;'
        )
        self.new_batch_button = QPushButton("New Batch")
        self.new_batch_button.setStyleSheet("""
            background-color: blue;
            color: #fff;
            border-radius: 5px;
            padding: 5px 10px;
            font-size: 16px;
        """)
        self.new_batch_button.clicked.connect(self.get_password)
        
        self.batch_label = QLabel('Batch Number:')
        self.batch_box = QComboBox()
        self.populate_batch_box()
        
       
        self.send_button = QPushButton(self)
        self.send_button.setText('Send Customer ID 🡺')
        self.send_button.setStyleSheet(
            'background: blue;'+
            'height: 24px;'+
            'font-size: 14px;'+
            'color: #fff;'
        )
        
        self.send_button.clicked.connect(self.get_id_and_batch)
        # self.populate_table()
        
        # Submit event for 'Send CID' button
        self.send_button.clicked.connect(self.send_cid_thread)
        self.logs = QPlainTextEdit("Logs will display here...")
        self.logs.setFixedHeight(450)
        self.logs.setFixedWidth(600)
        self.logs.setReadOnly(True)
        self.table1 = QTableWidget()
        self.table1.setColumnCount(3)
        self.table1.setRowCount(0)
        headers = ['Id number', 'Device id', 'Batch number']
        self.table1.setFixedHeight(450)
        self.table1.setFixedWidth(600)
        self.table1.setHorizontalHeaderLabels(headers)
        # make the header stretch to fill the whole width of the table
        self.table1.horizontalHeader().setStretchLastSection(True)
        self.table1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout = QHBoxLayout()
        layout.addWidget(self.table1)
        widget = QWidget()
        widget.setLayout(layout)
        
        # Progress bar 
        self.progress = ProgressBar(initial_value=0)
        self.progress.hide()
        # Grid layout for Device setup page
        self.main.addLayout(self.sim1_select.layout, 0,0)
        self.main.addLayout(self.sim2_select.layout, 0,1)
        self.main.addLayout(self.system_type_select.layout, 0,2)
        self.main.addWidget(self.customer_id, 1,0,1,3)
        self.main.addWidget(self.send_button, 2,0,1,3)
        self.main.addWidget(self.progress, 3, 0,1,3)
        logs_and_table_layout = QHBoxLayout()
        logs_and_table_layout.addWidget(self.logs)
        logs_and_table_layout.addWidget(self.table1)
        self.main.addLayout(logs_and_table_layout, 4,0,1,3)
        self.main.addWidget(self.new_batch_button)
        self.new_batch_button.setFixedWidth(400)
        self.main.addWidget(self.batch_label)
        self.main.addWidget(self.batch_box)
        self.batch_box.setFixedWidth(700)
        self.setLayout(self.main)
        # Connecting the Pyqt signals to events
        self.setupComPortSignal.connect(self.setup_com_port)
        self.sendCustomerIdSignal.connect(self.send_customer_id)
        self.sendClientCertificateSignal.connect(self.send_client_certificate)
        self.sendPrivateKeySignal.connect(self.send_private_key)
        self.sendEnergyDataSignal.connect(self.send_energy_data)
        self.sendNetwork1ConfigurationSignal.connect(self.send_network_1_configuration)
        self.sendNetwork2ConfigurationSignal.connect(self.send_network_2_configuration)
        self.sendSystemTypeConfigurationSignal.connect(self.send_system_type_configuration)
        self.setLayout(self.main)
        # Connecting the Pyqt signals to events
        self.setupComPortSignal.connect(self.setup_com_port)
        self.sendCustomerIdSignal.connect(self.send_customer_id)
        self.sendClientCertificateSignal.connect(self.send_client_certificate)
        self.sendPrivateKeySignal.connect(self.send_private_key)
        self.sendEnergyDataSignal.connect(self.send_energy_data)
        self.sendNetwork1ConfigurationSignal.connect(self.send_network_1_configuration)
        self.sendNetwork2ConfigurationSignal.connect(self.send_network_2_configuration)
        self.sendSystemTypeConfigurationSignal.connect(self.send_system_type_configuration)
        self.completedSetupSignal.connect(self.completed_setup)
        self.exceptionSignal.connect(self.process_exception)

    def select_sim1_handler(self,x)->None:
        """
            Description: Triggered event when SIM1 select input is changed
        """

        print(f"[SELECTED SIM1]: {x}")
        if x != len(self.network_names):  # Index of Other SIM option
            self.sim1 = self.network_names[x]
            self.network1_format='sim'
        else:
            self.sim1_apn_form = APNFormDialog()
            self.sim1_apn_form.submit_button.clicked.connect(self.sim1_apn_form_handler)
            self.sim1_apn_form.exec_()

    def select_sim2_handler(self,x)->None:
        """
            Description: Triggered event when SIM2 select input is change
        """
        print(f"[SELECTED SIM2]: {x}")
        if x != len(self.network_names):
            self.network2_format='sim'
            self.sim2 = self.network_names[x]
        else:
            self.sim2_apn_form = APNFormDialog()
            self.sim2_apn_form.submit_button.clicked.connect(self.sim2_apn_form_handler)
            self.sim2_apn_form.exec_()
    
    def sim1_apn_form_handler(self)->None:
        print(self.sim1_apn_form.apn_form_input.input.text())
        self.sim1 = self.sim1_apn_form.apn_form_input.input.text()
        self.network1_format='apn'
        self.sim1_apn_form.close()

    def sim2_apn_form_handler(self)->None:
        print(self.sim2_apn_form.apn_form_input.input.text())
        self.sim2 = self.sim2_apn_form.apn_form_input.input.text()
        self.network2_format='apn'
        self.sim2_apn_form.close()

    def select_system_type_handler(self,x)->None:
        """
            Description: Triggered event handler when SYSTEM TYPE select input is changed
        """
        print(f"[SELECTED SYSTEM_TYPE]: {x}")
        self.system_type = config["SYSTEM_TYPES"][x]


    def send_cid(self)->None:
        """
            Description: Main function for sending CID
        """
        self.cid = self.customer_id.text()
        self.progress.setValue(0)
        print(self.cid)
        print(format_flash_network(self.sim1,1,self.network1_format))
        print(format_flash_network(self.sim2,2,self.network2_format))
        print(format_system_type(self.system_type))
        print(self.network1_format)
        print(self.network2_format)
        try:
            # Fetch the device details for the solarbase API
            response_data = fetch_device_details(self.cid)
            print(response_data)
            self.thing_name= response_data["ThingCreation"]["thingName"]
            self.thing_arn= response_data["ThingCreation"]["thingArn"]
            self.thing_id=response_data["ThingCreation"]["thingId"]
            self.client_certificate=response_data["CertCreation"]["certificatePem"]
            self.public_key=response_data["CertCreation"]["keyPair"]["PublicKey"]
            self.private_key=response_data["CertCreation"]["keyPair"]["PrivateKey"]
            print(format_flash_certificate(self.client_certificate))
            print(len(format_flash_certificate(self.client_certificate)))

            print(format_flash_private_key(self.private_key))
            print(len(format_flash_private_key(self.private_key)))

            # Connect to EMS device via pyserial on a COM port
            if not self.device:
                ports = [port[0] for port in serial.tools.list_ports.grep("0483:5740")]
                self.device = serial.serial_for_url(ports[0], 115200, serial.EIGHTBITS, serial.PARITY_NONE,serial.STOPBITS_ONE,0,rtscts=1, write_timeout=10)
                self.device.timeout = 10  #10 seconds timeout 
                self.device.flushInput() # flush input buffer, discarding all its contents
                self.device.flushOutput() # flush output buffer, aborting current output
                


                # self.send_string('120', batch)   
            # gen_day = response_data["LastData"]["Data"][0]["GnT"]
            # gen_week = response_data["LastData"]["Data"][0]["GnW"]
            # gen_month = response_data["LastData"]["Data"][0]["GnM"]
            # gen_year = response_data["LastData"]["Data"][0]["GnY"]

            # con_off_day = response_data["LastData"]["Data"][0]["ConTfGd"]
            # con_off_week = response_data["LastData"]["Data"][0]["ConWfGd"]
            # con_off_month = response_data["LastData"]["Data"][0]["ConMfGd"]
            # con_off_year = response_data["LastData"]["Data"][0]["ConYfGd"]

            # con_on_day = response_data["LastData"]["Data"][0]["ConTOGd"]
            # con_on_week = response_data["LastData"]["Data"][0]["ConWOGd"]
            # con_on_month = response_data["LastData"]["Data"][0]["ConMOGd"]
            # con_on_year = response_data["LastData"]["Data"][0]["ConYOGd"]

            # peak_day = response_data["LastData"]["Data"][0]["PkT"]
            # peak_week = response_data["LastData"]["Data"][0]["PkW"]
            # peak_month = response_data["LastData"]["Data"][0]["PkM"]
            # peak_year = response_data["LastData"]["Data"][0]["PkY"]
            self.setupComPortSignal.emit(self.cid)
            time.sleep(10)
            self.sendCustomerIdSignal.emit(self.cid)
            time.sleep(10)
            self.sendClientCertificateSignal.emit()
            time.sleep(20)
            self.sendPrivateKeySignal.emit()
            time.sleep(20)
            self.sendNetwork1ConfigurationSignal.emit()
            time.sleep(20)
            self.sendNetwork2ConfigurationSignal.emit()
            time.sleep(20)
            self.sendSystemTypeConfigurationSignal.emit()
            time.sleep(10)
            self.sendEnergyDataSignal.emit()
            time.sleep(2)
            self.completedSetupSignal.emit()
        except Exception as e:
           print(e)
           if(str(e) == 'list index out of range'):
               self.exceptionSignal.emit("Could not find a connected Device \n(1)Remove USB cord \n(2)Make sure the Board is on\n(3)Connect USB properly\n")
           else:
               self.exceptionSignal.emit("Could not connect to the internet.")

    # Event signals - uses multithreading to prevent lagging of the GUI
    def setup_com_port(self, cid:str)->None:
        """
            Description: Check COM Port, Preliminary test
        """
        self.progress.show()
        self.logs.clear()
        print("Checking COM Port...")
        self.logs.appendPlainText(format_log(f"Checking COM Port..."))
        self.logs.appendPlainText(format_log(f"Found device on PORT : {self.device.portstr}"))
        flash_id = "107"+cid+"\0"
        self.logs.appendPlainText(format_log("Clearing Flash Memory.."))
        self.device.write(flash_id.encode())
        result = str(self.device.read(10))
        if result.find("NoResp") != -1:
            self.logs.appendPlainText("[ERROR]: Failed to clear flash memory.")
        self.progress.setValue(10)

    # Send Customer ID to the flash memory
    def send_customer_id(self, cid:str)->None:
        """
            Description: Send CID to the EMS device for initial configuration
        """
        print("Customer ID sending function...")
        self.logs.appendPlainText(format_log("Sending Customer ID..."))
        print(f"Writing: {format_flash_cid(cid)}")
        self.device.write(format_flash_cid(cid).encode())
        result = str(self.device.read(10))
        if result.find("NoResp") != -1:
            self.logs.appendPlainText("[ERROR]: Failed to send Customer ID")
        self.progress.setValue(20)
        self.logs.appendPlainText(format_log("[SUCCESS]: Sending Customer ID successful."))
        

    # Get Board ID to the flash memory
    def get_board_id(self, bid:str)->None:
        """
            Description: Get BID from the EMS device for initial configuration
        """
        print("Board ID sending function...")
        self.logs.appendPlainText(format_log("Getting Board ID..."))
        print(f"Writing: {format_flash_cid(bid)}")
        self.device.write(format_flash_cid(bid).encode())
        result = str(self.device.read(10))
        if result.find("NoResp") != -1:
            self.logs.appendPlainText("[ERROR]: Failed to Get Board ID")
        self.progress.setValue(20)
        self.logs.appendPlainText(format_log("[SUCCESS]: Board ID acquired successfully."))        

    # Send Client Certificate to the flash memory
    def send_client_certificate(self)->None:
        """
            Description: Send client certificate to the EMS device flash memory
        """
        #time.sleep(10)
        self.logs.appendPlainText(format_log("Sending Client Certificate..."))
        for chunk in format_flash_certificate(self.client_certificate):
            print(f"Writing: {chunk}")
            self.device.write(chunk.encode())
        result = str(self.device.read(10))
        if result.find("NoResp") != -1:
            self.logs.appendPlainText("[ERROR]: Failed to send Client Certificate")
        self.progress.setValue(40)
        self.logs.appendPlainText(format_log("[SUCCESS]: Sending Client Certificate successful."))

    # Send Private key to the flash memory
    def send_private_key(self)->None:
        """
            Description: Send private key to the EMS device flash memory
        """
        self.logs.appendPlainText(format_log("Sending Private Key..."))
        for chunk in format_flash_private_key(self.private_key):
            print(f"Writing: {chunk}")
            self.device.write(chunk.encode())
        result = str(self.device.read(10))
        if result.find("NoResp") != -1:
            self.logs.appendPlainText("[ERROR]: Failed to send Private Key")
        self.progress.setValue(60)
        self.logs.appendPlainText(format_log("[SUCCESS]: Sending Private Key successful."))

    # Send network 1 configuration to flash memory
    def send_network_1_configuration(self)->None:
        """
            Description: Send SIM1 network APN configuration to the EMS device
        """
        self.logs.appendPlainText(format_log("Sending Dual SIM Configuration....."))
        print(f"Writing: {format_flash_network(self.sim1,1,self.network1_format)}")
        self.device.write(format_flash_network(self.sim1, 1,self.network1_format).encode())
        result = str(self.device.read(10))
        if result.find("NoResp") != -1:
            self.logs.appendPlainText("[ERROR]: Failed to send Dual SIM configuration")
        self.progress.setValue(70)

    # Send network 2 configuration to flash memory 
    def send_network_2_configuration(self)->None:
        """
            Description: Send SIM2 network APN configuration to the EMS device
        """
        print(f"Writing: {format_flash_network(self.sim2,2,self.network2_format)}")
        self.device.write(format_flash_network(self.sim2, 2,self.network2_format).encode())
        result = str(self.device.read(10))
        if result.find("NoResp") != -1:
            self.logs.appendPlainText("[ERROR]: Failed to send Dual SIM configuration")
        self.progress.setValue(80)
        self.logs.appendPlainText(format_log("[SUCCESS]: Sending DUAL SIM configuration successful."))

    # Send system type configuration to flash memory 
    def send_system_type_configuration(self)->None:
        """
            Description: Send System Type configuration to the EMS device
        """
        self.logs.appendPlainText(format_log("Sending System Type Configuration..."))
        print(f"Writing: {format_system_type(self.system_type)}")
        self.device.write(format_system_type(self.system_type).encode())
        result = str(self.device.read(10))
        if result.find("NoResp") != -1:
            self.logs.appendPlainText("[ERROR]: Failed to send system type configuration")
        self.progress.setValue(90)
        self.logs.appendPlainText(format_log("[SUCCESS]: Sending System Type configuration successful."))
    
    # Send energy data to the flash memory
    def send_energy_data(self)->None:
        """
            Description: Send energy data
        """
        with open("./test-file.txt", "a+") as f:
            self.logs.appendPlainText(format_log("Sending Energy Data......"))
            f.write("Energy data:")
        f.close()
        self.progress.setValue(100)

    # Completed
    def completed_setup(self)->None:
        """
            Description: Trigger notification dialog for successful completion
        """
        self.device.close()
        self.device = None
        self.logs.appendHtml(format_log('<b>DONE 🎉🎉</b>'))
        completed_dialog=MessageBox(text="Device Successfully Configured.",mode="information")
        completed_dialog.exec_()

    # Exception
    def process_exception(self, information:str=None)->None:
        exception_dialog=MessageBox(text="An Error occurred.", mode="critical", information=information)
        exception_dialog.exec_()

    def send_cid_thread(self):
        """
            Description: Start the main thread 
        """
        self.threadpool = QThreadPool()
        print(self.threadpool.maxThreadCount())
        self.worker = Worker(self.send_cid)
        self.threadpool.start(self.worker)
    def get_password(self):
        """
            Description: Get password from the user
        """
        password, ok = QInputDialog.getText(self, 'Password', 'Enter password:',QLineEdit.Password)
        if not ok:
            return None
        
        if password != 'mypassword':
            QMessageBox.warning(self, 'Error', 'Wrong password')
            return
        batch_number, ok = QInputDialog.getText(self, 'Batch number', 'Enter batch number:')
        if not ok:
            return
        # if the batch number is not in the database, add it to the database and the combobox else use Qmessagebox to show error
        if batch_number not in [self.batch_box.itemText(i) for i in range(self.batch_box.count())]:
            self.c.execute('INSERT INTO id_batch (batch_Snumber) VALUES (?)', (batch_number,))
            self.conn.commit()
            self.batch_box.addItem(batch_number)
            QMessageBox.information(self, 'Success', 'Batch number added')
        else:
            QMessageBox.warning(self, 'Error', 'Batch number already exists')
            return

    def get_id_and_batch(self):
        """
        Description: Get the id and batch number from the database"""

        matching_ports = [port[0] for port in serial.tools.list_ports.grep("0483:5740")]
        port = matching_ports[0]
        self.serial = serial.Serial(port, baudrate=115200, timeout=10, rtscts=1, write_timeout=10)
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        self.polulate_table()
        self.get_serial_number('120', self.batch_box.currentText())
        self.serial.close()

    def get_serial_number(self, string, batch_number):
        """
        Description: Get the serial number from the EMS Board"""
        # generate uid string
        sent_string = string 
        # send string to EMS board
        self.serial.write(sent_string.encode())
        # read serial port
        serial_number = self.serial.readline().decode()
        serial_number_dict = json.loads(serial_number)
        # get serial number
        serial_number = serial_number_dict['BID']
        # get all serial number and batch number from database
        self.c.execute('SELECT serial_number, batch_Snumber FROM id_batch_serial_number')
        self.conn.commit()
        existing_text = self.c.fetchall()
        for i in existing_text:
            if serial_number in i:
                QMessageBox.warning(self, 'Error', 'UID already exists in database.')
                return
        self.c.execute('INSERT INTO id_batch_serial_number (serial_number, batch_Snumber) VALUES (?,?)', (serial_number, batch_number))
        self.conn.commit()
        QMessageBox.information(self, 'Success', 'UID added to database.')

    def populate_batch_box(self):
        """
            Description: Populate the batch box with the batch numbers from the database

        """
        self.c.execute('SELECT batch_Snumber FROM id_batch')
        self.conn.commit()
        batch_numbers = self.c.fetchall()
        for batch_number in batch_numbers:
            self.batch_box.addItem(batch_number[0])

    def polulate_table(self):
        """
            Description: Populate the table with the serial numbers and batch numbers from the database"""
        self.c.execute('SELECT * FROM id_batch_serial_number')
        self.conn.commit()
        data = self.c.fetchall()
        self.table1.setRowCount(0)
        for row_number, row_data in enumerate(data):
            self.table1.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table1.setItem(row_number, column_number, QTableWidgetItem(str(data)))


# Implementation of the Custom class for worker thread
class Worker(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        '''
            Description: Initialise the runner function with passed args, kwargs.
        '''
        self.fn(*self.args, **self.kwargs)

class APNFormDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(200)
        self.setMinimumWidth(350)
        self.setWindowTitle("Enter APN")
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(bundle_dir,'assets/images/arnergy-icon.png'))))

        self.apn_form_input = FormField(label="Enter APN",placeholder="Enter a valid APN")
        self.submit_button = QPushButton(self)
        self.submit_button.setText('Enter 🡺')
        self.submit_button.setStyleSheet(
            'background: blue;'+
            'height: 24px;'+
            'font-size: 14px;'+
            'color: #fff;'
        )
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.apn_form_input.layout)
        self.layout.addWidget(self.submit_button)
        self.setLayout(self.layout)


class Settings(SettingsDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.settings_dialog = SettingsDialog()
        self.set_system_type.activated.connect(self.set_system_type_handler)
        self.set_primary_sim.activated.connect(self.set_primary_sim_handler)
        self.set_secondary_sim.activated.connect(self.set_secondary_sim_handler)

    def set_system_type_handler(self,x)->None:
        global saved_settings
        print('Set system type:',x)
        saved_settings["SYSTEM_TYPE"]=x
    
    def set_primary_sim_handler(self,x)->None:
        global saved_settings
        print('Set Primary SIM: ',x)
        saved_settings["SIM1"]=x

    def set_secondary_sim_handler(self,x)->None:
        global saved_settings
        print('Set secondary SIM: ',x)
        saved_settings["SIM2"]=x

if __name__ == "__main__":
    # To set the style of the application
    app = QApplication(sys.argv)
    win = EMSFlasherApp()
    # Execute the application main window
    win.show()
    sys.exit(app.exec_())
