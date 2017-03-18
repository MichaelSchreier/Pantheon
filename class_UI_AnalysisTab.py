from PyQt5 import QtGui, QtCore, QtWidgets

class AnalysisTab():
	"""
	Class that stores the UI elements (and their layout) for analysing the simulation
	results.
	"""
	def __init__(self):
		#UI elements----------------------------------------------------
		label_determine_orbital_period = QtWidgets.QLabel(
			"select bodies to calculate the orbital period of the satellite around the central body"
		)
		
		self.combobox_central_body = QtWidgets.QComboBox()
		label_central_body = QtWidgets.QLabel("central body")
		
		self.combobox_satellite_body = QtWidgets.QComboBox()
		label_satellite_body = QtWidgets.QLabel("satellite body")
		
		self.updateAnalysisComboboxes()
		
			
		self.button_calculate_period = QtWidgets.QPushButton('calculate orbital period')
		self.lineedit_orbital_period = QtWidgets.QLineEdit()
		self.lineedit_orbital_period.setReadOnly(True)
		
		#layout---------------------------------------------------------
		self.layout = QtWidgets.QGridLayout()
		self.layout.addWidget(label_determine_orbital_period, 0, 0, 1, 0)
		self.layout.addWidget(label_central_body, 1, 0)
		self.layout.addWidget(self.combobox_central_body, 1, 1)
		self.layout.addWidget(label_satellite_body, 2, 0)
		self.layout.addWidget(self.combobox_satellite_body, 2, 1)
		self.layout.setRowStretch(3, 5)
		self.layout.addWidget(self.button_calculate_period, 4, 0)
		self.layout.addWidget(self.lineedit_orbital_period, 4, 1)
		
		
	def updateAnalysisComboboxes(self, plotobjects=[]):
		"""
		refreshes the list of possible plot origins
		"""
		self.combobox_central_body.clear()
		self.combobox_satellite_body.clear()
		for item in plotobjects:
			self.combobox_central_body.addItem(item)
			self.combobox_satellite_body.addItem(item)