# -*- coding: utf-8 -*-
# TFTPUI is the GUI version of the TFTP tool for Guest boards based on Step Platform.
# It can be used to fetch and display the TFTP file from the Guest board.
# The GUI is based on QT, TFTP based on Curl, plotting on Matplotlib.

import sys
import os
import time
import subprocess
import re
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from ui import Ui_Dialog
from struct import unpack_from
from base import tftplib
from base import cop
from pddm5 import PDDM5

class TftpDialog(QDialog):
	# Signal used to send the tftp file name to the guest boards.
	Signal=QtCore.pyqtSignal(str,str)  # board type + tftp file name
	
	def __init__(self):
		super(TftpDialog, self).__init__()

		# Set up the user interface from Designer.
		self.ui = Ui_Dialog()
		self.ui.setupUi(self)
				
		# Connect the button click signals.
		self.ui.pushButton_Ping.clicked.connect(self.Ping)
		self.ui.pushButton_Clear.clicked.connect(self.ClearLog)
		self.ui.pushButton_Fetch.clicked.connect(self.Fetch)
		self.ui.pushButton_Show.clicked.connect(self.BigShow)
		self.ui.pushButton_FetchShow.clicked.connect(self.FetchAndShow)
		self.ui.pushButton_Manual.clicked.connect(self.Manual)
		
		# Define the ComboBox content
		self.ui.comboBox_RackNo.addItems(['1', '2', '3'])
		self.ui.comboBox_SlotNo.addItems(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15'])
		self.ui.comboBox_CPU.addItems(['A', 'B'])
		# TODO: add items for other Guest Boards.
		self.ui.comboBox_Type.addItems(['PDDM46', 'PDDM5'])
		
		# Connect the comboBox select signal
		self.ui.comboBox_Type.currentIndexChanged.connect(self.AddItemToFileCombo)
		
		# TODO: Connect the tftp file signal
		self.pddm5 = PDDM5('PDDM5', 1)
		self.pddm5.deviceInit(msgFile = r'./config/pddm5_message.xml', \
							 log = r'./log/pddm5.log')
		self.Signal.connect(self.pddm5.fileParser)
		self.pddm5.Signal.connect(self.Log)

	def AddItemToFileCombo(self):
		self.ui.comboBox_Name.clear()
		
		# TODO: add ftp_* for other Guest Board.
		if self.ui.comboBox_Type.currentText() == 'PDDM5':
			self.ui.comboBox_Name.addItems(['ftp_vers', 'ftp_phase', 'ftp_volt', 'ftp_indi', 'ftp_err'])
		elif self.ui.comboBox_Type.currentText() == 'PDDM46':
			self.ui.comboBox_Name.addItems(['ftp_vers', 'ftp_cur', 'ftp_indi', 'ftp_err'])
			
	def IPCheck(self, key):
		pattern = "\\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\b"
		if re.match(pattern, key) != None:
			return True
		else:
			return False

	def Ping(self):
		# Check if the ip address is valid
		if self.IPCheck(self.ui.lineEdit_IP.text()) == True:
			p = subprocess.Popen("ping -n 2 " + self.ui.lineEdit_IP.text(),stdout=subprocess.PIPE)
			output = p.stdout.read()
			self.Log(output)
			p.terminate()
		else: 
			self.Log("Ilegal IP")
		
	def Fetch(self):
		rack = int(self.ui.comboBox_RackNo.currentText())
		slot = int(self.ui.comboBox_SlotNo.currentText())
		cpu  = self.ui.comboBox_CPU.currentText()
		ip = self.ui.lineEdit_IP.text()
		file = self.ui.comboBox_Name.currentText()
		
		if self.IPCheck(ip) == False:
			self.Log("Ilegal IP")
			return -1
		
		# Enable the routing to the corresponding Guest board.
		status, copopen_errinfo = cop.CopOpen(rack, slot, cpu, ip)
		
		if status != 0:
			self.Log('copopen status: ' + str(status) + ', errinfo: ' + copopen_errinfo)
		else:
			self.Log('copopen status: ' + str(status))
			# DownLoad the tftp file.
			status, download_errinfo = tftplib.Tftplib_Download(rack, slot, cpu, file, ip)
			if status == 0:
				self.Log('download status: ' + str(status))
			else:
				self.Log('download status: ' + str(status) + ', errinfo: ' + download_errinfo)
		return status
		
	def BigShow(self):
		fileName = QFileDialog.getOpenFileName()
		self.Log(fileName[0])
		self.Show(fileName[0])
		
	def Show(self, file):
		board = self.ui.comboBox_Type.currentText()

		if os.path.isfile(file):
			self.Signal.emit(board, file)
		else:
			self.Log(file + ' is not exist.')
		
	def FetchAndShow(self):
		if self.Fetch() == 0:
			self.Show(self.ui.comboBox_Name.currentText())

	def Log(self, str):
		self.ui.textEdit_Log.append(time.asctime(time.localtime(time.time())) + ' ---- ' + str)
		
	def ClearLog(self):
		self.ui.textEdit_Log.clear()
		
	def Manual(self):
		self.Log('Manual is unavailable...')
	
app = QApplication(sys.argv)
window = TftpDialog()
window.show()
sys.exit(app.exec_())
