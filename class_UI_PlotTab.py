from PyQt5 import QtGui, QtCore, QtWidgets

class PlotTab():
	"""
	Class that stores the UI elements (and their layout) for the plot parameters.
	"""
	def __init__(self):
		#UI elements----------------------------------------------------
		self.combobox_plot_origin = QtWidgets.QComboBox()
		label_plot_origin = QtWidgets.QLabel("plot motion relative to")
		self.updateOrigin()
		
		self.combobox_plot_plane = QtWidgets.QComboBox()
		self.combobox_plot_plane.addItem("XY")
		self.combobox_plot_plane.addItem("YZ")
		self.combobox_plot_plane.addItem("XZ")
		label_plot_plane = QtWidgets.QLabel("plotting plane")
		
		self.button_update_plot = QtWidgets.QPushButton('update plot')
		
		#layout---------------------------------------------------------
		self.layout_plot_settings = QtWidgets.QVBoxLayout()
		self.layout_plot_settings.addWidget(label_plot_origin)
		self.layout_plot_settings.addWidget(self.combobox_plot_origin)
		self.layout_plot_settings.addWidget(label_plot_plane)
		self.layout_plot_settings.addWidget(self.combobox_plot_plane)
		self.layout_plot_settings.insertStretch(-1)
		self.layout_plot_settings.addWidget(self.button_update_plot)
		
		
	def updateOrigin(self, plotobjects=[]):
		"""
		refreshes the list of possible plot origins
		"""
		self.combobox_plot_origin.clear()
		self.combobox_plot_origin.addItem("origin")
		for item in plotobjects:
			self.combobox_plot_origin.addItem(item)