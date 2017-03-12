from PyQt5 import QtGui, QtCore, QtWidgets

class ParameterTab():
	"""
	Class that stores the UI elements (and their layout) for the general object parameters.
	"""
	def __init__(self):
		#TreeView-------------------------------------------------------
		self.objects_tree = QtWidgets.QTreeWidget()
		self.objects_tree.setMinimumSize(QtCore.QSize(200, 50))
		self.objects_tree.setHeaderLabel("object")

		
		#define initial position----------------------------------------
		self.label_x_initial = QtWidgets.QLabel("x")
		self.spinbox_x_initial = QtWidgets.QDoubleSpinBox()
		self.spinbox_x_initial.setSuffix(" m")
		self.spinbox_x_initial.setFixedWidth(100)
		self.spinbox_x_initial.setRange(-1e15,1e15)
		#self.spinbox_x_initial.setDecimals(0)
		
		self.label_y_initial = QtWidgets.QLabel("y")
		self.spinbox_y_initial = QtWidgets.QDoubleSpinBox()
		self.spinbox_y_initial.setSuffix(" m")
		self.spinbox_y_initial.setFixedWidth(100)
		self.spinbox_y_initial.setRange(-1e15,1e15)
		#self.spinbox_y_initial.setDecimals(0)
		
		self.label_z_initial = QtWidgets.QLabel("z")
		self.spinbox_z_initial = QtWidgets.QDoubleSpinBox()
		self.spinbox_z_initial.setSuffix(" m")
		self.spinbox_z_initial.setFixedWidth(100)
		self.spinbox_z_initial.setRange(-1e15,1e15)
		#self.spinbox_z_initial.setDecimals(0)
		
		layout_position_initial = QtWidgets.QGridLayout()
		layout_position_initial.addWidget(self.label_x_initial, 1, 1)
		layout_position_initial.addWidget(self.label_y_initial, 2, 1)
		layout_position_initial.addWidget(self.label_z_initial, 3, 1)
		layout_position_initial.addWidget(self.spinbox_x_initial, 1, 2)
		layout_position_initial.addWidget(self.spinbox_y_initial, 2, 2)
		layout_position_initial.addWidget(self.spinbox_z_initial, 3, 2)
		
		group_position_initial = QtWidgets.QGroupBox("initial position")
		group_position_initial.setLayout(layout_position_initial)
		
		
		#define initial speed-------------------------------------------
		self.label_vx_initial = QtWidgets.QLabel("v<sub>x</sub>")
		self.spinbox_vx_initial = QtWidgets.QDoubleSpinBox()
		self.spinbox_vx_initial.setSuffix(" m/s")
		self.spinbox_vx_initial.setFixedWidth(100)
		self.spinbox_vx_initial.setRange(-1e15,1e15)
		#self.spinbox_vx_initial.setDecimals(0)
		
		self.label_vy_initial = QtWidgets.QLabel("v<sub>y</sub>")
		self.spinbox_vy_initial = QtWidgets.QDoubleSpinBox()
		self.spinbox_vy_initial.setSuffix(" m/s")
		self.spinbox_vy_initial.setFixedWidth(100)
		self.spinbox_vy_initial.setRange(-1e15,1e15)
		#self.spinbox_vy_initial.setDecimals(0)
		
		self.label_vz_initial = QtWidgets.QLabel("v<sub>z</sub>")
		self.spinbox_vz_initial = QtWidgets.QDoubleSpinBox()
		self.spinbox_vz_initial.setSuffix(" m/s")
		self.spinbox_vz_initial.setFixedWidth(100)
		self.spinbox_vz_initial.setRange(-1e15,1e15)
		#self.spinbox_vz_initial.setDecimals(0)
		
		layout_velocity_initial = QtWidgets.QGridLayout()
		layout_velocity_initial.addWidget(self.label_vx_initial, 1, 1)
		layout_velocity_initial.addWidget(self.label_vy_initial, 2, 1)
		layout_velocity_initial.addWidget(self.label_vz_initial, 3, 1)
		layout_velocity_initial.addWidget(self.spinbox_vx_initial, 1, 2)
		layout_velocity_initial.addWidget(self.spinbox_vy_initial, 2, 2)
		layout_velocity_initial.addWidget(self.spinbox_vz_initial, 3, 2)
		
		group_velocity_initial = QtWidgets.QGroupBox("initial velocity")
		group_velocity_initial.setLayout(layout_velocity_initial)
		
		
		#name-----------------------------------------------------------
		self.lineedit_object_name = QtWidgets.QLineEdit()
		self.label_object_name = QtWidgets.QLabel("name")
		
		self.label_object_mass = QtWidgets.QLabel("mass")
		self.spinbox_object_mass = QtWidgets.QDoubleSpinBox()
		self.spinbox_object_mass.setFixedWidth(100)
		self.spinbox_object_mass.setSuffix(" kg")
		self.spinbox_object_mass.setRange(0,1e40)
		self.spinbox_object_mass.setDecimals(0)
		
		self.combobox_object_primary = QtWidgets.QComboBox()
		self.label_object_primary = QtWidgets.QLabel("satellite of") #or 'primary'
		self.label_object_primary.setToolTip("If a primary is selected, position and velocity are taken as relative to that object")
		self.combobox_object_primary.setToolTip("If a primary is selected, position and velocity are taken as relative to that object")
		
		layout_object_parameter = QtWidgets.QGridLayout()
		layout_object_parameter.addWidget(self.label_object_name, 1, 1)
		layout_object_parameter.addWidget(self.label_object_mass, 2, 1)
		layout_object_parameter.addWidget(self.lineedit_object_name, 1, 2)
		layout_object_parameter.addWidget(self.spinbox_object_mass, 2, 2)
		layout_object_parameter.setRowStretch(3, -1)
		layout_object_parameter.addWidget(self.label_object_primary, 4, 1)
		layout_object_parameter.addWidget(self.combobox_object_primary, 4, 2)
		
		group_object_parameter = QtWidgets.QGroupBox("general parameters")
		group_object_parameter.setLayout(layout_object_parameter)		
		
		
		#grid-----------------------------------------------------------
		layout_object_container = QtWidgets.QGridLayout()
		layout_object_container_1 = QtWidgets.QGridLayout()
		layout_object_container_1.addWidget(group_object_parameter, 1, 1)
		layout_object_container_2 = QtWidgets.QGridLayout()
		layout_object_container_2.addWidget(group_position_initial, 1, 1)
		layout_object_container_2.addWidget(group_velocity_initial, 2, 1)
		layout_object_container.addLayout(layout_object_container_1, 1, 1)
		layout_object_container.addLayout(layout_object_container_2, 1, 2)
			
			
		#buttons--------------------------------------------------------
		self.button_add_object = QtWidgets.QPushButton('add')
		self.button_edit_object = QtWidgets.QPushButton('edit')
		self.button_delete_object = QtWidgets.QPushButton('delete')
		
		layout_object_buttons = QtWidgets.QVBoxLayout()
		layout_object_buttons.addWidget(self.button_add_object)
		layout_object_buttons.addWidget(self.button_edit_object)
		layout_object_buttons.addWidget(self.button_delete_object)
		layout_object_buttons.insertStretch(-1)		
		
		self.layout_parameter_container = QtWidgets.QHBoxLayout()
		self.layout_parameter_container.addWidget(self.objects_tree)
		self.layout_parameter_container.addLayout(layout_object_buttons)
		self.layout_parameter_container.addLayout(layout_object_container)
		self.layout_parameter_container.insertSpacing(1,20)
		self.layout_parameter_container.insertSpacing(3,20)
