from PyQt5 import QtGui, QtCore, QtWidgets

class SimulationTab():
	"""
	Class that stores the UI elements (and their layout) for the simulation parameters.
	"""
	def __init__(self):
		#UI elements----------------------------------------------------
		self.spinbox_delta_time = QtWidgets.QDoubleSpinBox()
		self.spinbox_delta_time.setSuffix(" s")
		self.spinbox_delta_time.setFixedWidth(100)
		self.spinbox_delta_time.setRange(1, 1e7)
		self.spinbox_delta_time.setSingleStep(3600)
		self.spinbox_delta_time.setValue(86400)
		self.spinbox_delta_time.setDecimals(0)
		label_delta_time = QtWidgets.QLabel("time step")
		
		self.spinbox_time_steps = QtWidgets.QDoubleSpinBox()
		self.spinbox_time_steps.setFixedWidth(100)
		self.spinbox_time_steps.setRange(1, 1e8)
		self.spinbox_time_steps.setSingleStep(1)
		self.spinbox_time_steps.setValue(365)
		self.spinbox_time_steps.setDecimals(0)
		label_time_steps = QtWidgets.QLabel("number of time steps")
		
		self.spinbox_total_time = QtWidgets.QDoubleSpinBox()
		self.spinbox_total_time.setSuffix(" s")
		self.spinbox_total_time.setFixedWidth(100)
		self.spinbox_total_time.setRange(1, 1e15)
		self.spinbox_total_time.setSingleStep(3600*24)
		self.spinbox_total_time.setValue(3600*24*365)
		self.spinbox_total_time.setDecimals(0)
		label_total_time = QtWidgets.QLabel("total time")
		
		self.spinbox_skip_n = QtWidgets.QSpinBox()
		self.spinbox_skip_n.setFixedWidth(100)
		self.spinbox_skip_n.setRange(1, 1e6)
		self.spinbox_skip_n.setSingleStep(1)
		self.spinbox_skip_n.setValue(1)
		label_skip_n = QtWidgets.QLabel("output simulation result for every nth step")
			
		self.checkbox_openCL = QtWidgets.QCheckBox('use OpenCL')
		label_openCL = QtWidgets.QLabel("run simulation on GPU")
		
		self.combobox_method = QtWidgets.QComboBox()
		self.combobox_method.addItem("first order leapfrog (fast)")
		self.combobox_method.addItem("PEFRL (accurate)")
		label_method = QtWidgets.QLabel("select algorithm")
		
		self.button_start_simulation = QtWidgets.QPushButton('run simulation')
		self.button_stop_simulation = QtWidgets.QPushButton('stop simulation')
		
		#layout---------------------------------------------------------
		self.layout_simulation_settings = QtWidgets.QGridLayout()
		self.layout_simulation_settings.addWidget(label_delta_time, 1, 1)
		self.layout_simulation_settings.addWidget(self.spinbox_delta_time, 1, 2)
		self.layout_simulation_settings.addWidget(label_total_time, 2, 1)
		self.layout_simulation_settings.addWidget(self.spinbox_total_time, 2, 2)
		self.layout_simulation_settings.addWidget(label_time_steps, 3, 1)
		self.layout_simulation_settings.addWidget(self.spinbox_time_steps, 3, 2)
		self.layout_simulation_settings.addWidget(label_skip_n, 4, 1)
		self.layout_simulation_settings.addWidget(self.spinbox_skip_n, 4, 2)
		self.layout_simulation_settings.addWidget(label_openCL, 5, 1)
		self.layout_simulation_settings.addWidget(self.checkbox_openCL, 5, 2)
		self.layout_simulation_settings.addWidget(label_method, 6, 1)
		self.layout_simulation_settings.addWidget(self.combobox_method, 6, 2)
		
		self.layout_simulation_settings_container = QtWidgets.QVBoxLayout()
		self.layout_simulation_settings_container.addLayout(self.layout_simulation_settings)
		self.layout_simulation_settings_container.insertStretch(-1)
		self.layout_simulation_settings_container.addWidget(self.button_start_simulation)
		self.layout_simulation_settings_container.addWidget(self.button_stop_simulation)