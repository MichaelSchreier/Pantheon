import sys
import os
import psutil

import numpy as np
from scipy.fftpack import rfft, fftfreq

import pyqtgraph as pg
import pyopencl as cl

from PyQt5 import QtCore, QtWidgets, QtGui
from queue import Queue
from threading import Thread

from methods_colors import givecolor
from methods_simulation import threadedSimulation
from class_AstronomicalObject import AstronomicalObject
from class_UI_ParameterTab import ParameterTab
from class_UI_SimulationTab import SimulationTab
from class_UI_PlotTab import PlotTab
from class_UI_AnalysisTab import AnalysisTab
from class_UI_AboutWindow import aboutDialog

#-----------------------------------------------------------------------
pg.setConfigOption("background", "k")
#-----------------------------------------------------------------------


class PantheonMainWindow(QtWidgets.QMainWindow):
	"""
	Defines general window geometry and menu bar behavior.
	"""
	def __init__(self):
		super(PantheonMainWindow, self).__init__()
		self.initUI()
	 
	 
	def initUI(self):
		#General stuff
		self.setGeometry(200, 200, 100, 100)#the latter two numbers ensure the smallest possible window size on startup
		self.setWindowTitle('Pantheon')
		
		#Status Bar
		self.status_msg = QtWidgets.QLabel("Ready")
		self.statusBar().addWidget(self.status_msg, 1)
		
		self.progress_bar = QtWidgets.QProgressBar()
		self.progress_bar.setRange(0, 100)
		self.progress_bar.setValue(0)
		self.statusBar().addWidget(self.progress_bar, 1)
		self.progress_bar.hide()
		
		#createUI
		self.main_widget = PantheonCentralWidget(self)
		self.setCentralWidget(self.main_widget)
		
		#Menu Bar
		action_exit = QtGui.QAction(QtGui.QIcon("exit.png"), '&Exit', self)
		action_exit.setShortcut('Ctrl+Q')
		action_exit.setStatusTip('Exit application')
		action_exit.triggered.connect(self.close)
		
		action_save = QtGui.QAction(QtGui.QIcon("save.png"), '&Save', self)
		action_save.setShortcut('Ctrl+S')
		action_save.setStatusTip('Save object list')
		action_save.triggered.connect(self.main_widget.save)
		
		action_load = QtGui.QAction(QtGui.QIcon("load.png"), '&Load', self)
		action_load.setShortcut('Ctrl+L')
		action_load.setStatusTip('Load object list')
		action_load.triggered.connect(self.main_widget.load)
		
		action_about = QtGui.QAction(QtGui.QIcon("about.png"), '&About', self)
		action_about.setShortcut('Ctrl+A')
		action_about.setStatusTip('Display licenses')
		action_about.triggered.connect(self.openAboutDialog)
		
		menu_bar = self.menuBar()
		menu_file = menu_bar.addMenu('&File')
		menu_file.addAction(action_save)
		menu_file.addAction(action_load)
		menu_file.addAction(action_exit)		
		menu_about = menu_bar.addMenu('&Help')
		menu_about.addAction(action_about)
		
		self.show()
		
		
	def openAboutDialog(self):
		self.about = aboutDialog()
		self.about.show()
		

class PantheonCentralWidget(QtWidgets.QWidget):
	"""
	Main class which ties together the different UI elements and defines button behavior 
	as well as providing the framework in which the actual simulation is running.
	"""
	def __init__(self, parent):
		super(PantheonCentralWidget, self).__init__()
		self.initUI()
		self._data_plot = [[],[]]
		self._parent = parent
		
	
	def setPlotData(self, data_plot):
		self._data_plot = data_plot
	
	
	def getPlotData(self):
		return self._data_plot
	   
		
	def initUI(self):
		#list of nodes and properties
		self.object_list = []
		self.queue_data = Queue(maxsize=0)
		self.queue_comm = Queue(maxsize=1)
		
		self.timer = QtCore.QTimer(self)
		self.timer.setInterval(100)
		self.timer.timeout.connect(self.checkQueues)
		self.timer.start()
		
		self.simulation_running = False
		

		#setting up UI elements
		#-------first container_tab-----------------------------------------------
		self.tab_objects = ParameterTab()
		self.updatePrimaryList()
		
		#-------second container_tab----------------------------------------------
		self.tab_simulation = SimulationTab()
		
		#-------third container_tab-----------------------------------------------
		self.tab_plot = PlotTab()
		
		#-------fourth container_tab----------------------------------------------
		self.tab_analysis = AnalysisTab()
		
		
		container_tab = QtWidgets.QTabWidget()
		container_tab.setFixedHeight(250)
		tab1 = QtWidgets.QWidget()
		tab1.setLayout(self.tab_objects.layout_parameter_container)
		tab2 = QtWidgets.QWidget()
		tab2.setLayout(self.tab_simulation.layout_simulation_settings_container)
		tab3 = QtWidgets.QWidget()
		tab3.setLayout(self.tab_plot.layout_plot_settings)
		tab4 = QtWidgets.QWidget()
		tab4.setLayout(self.tab_analysis.layout)
		container_tab.addTab(tab1, "object settings")
		container_tab.addTab(tab2, "simulation settings")
		container_tab.addTab(tab3, "plot settings")
		container_tab.addTab(tab4, "orbital analysis")
		
		#pyqtgraph------------------------------------------------------
		graph = pg.GraphicsLayoutWidget()
		#graph.setFixedHeight(400)
		graph.setMinimumHeight(400)
		
		self.plot = graph.addPlot()
		self.plot.addLegend()#the argument (width, height) should also be set...
		self.plot.showAxis("right")
		self.plot.showAxis("top")
		self.plot.getAxis("bottom").setLabel(text="x", units="m")
		self.plot.getAxis("left").setLabel(text="y", units="m")
		self.plot.showGrid(x=True, y=True)
		self.plot.setAspectLocked(lock=True, ratio=1)
		#---------------------------------------------------------------
		
		main_layout = QtWidgets.QVBoxLayout()
		main_layout.addWidget(container_tab)
		main_layout.addWidget(graph)	
		self.setLayout(main_layout)
			
		self.show()
		
		
		#UI interaction-----------------------------------------------------
		self.tab_objects.button_delete_object.clicked.connect(self.deleteSelectedObject)
		self.tab_objects.button_add_object.clicked.connect(self.addBody)
		self.tab_objects.button_edit_object.clicked.connect(self.editObject)
		self.tab_simulation.button_start_simulation.clicked.connect(self.enqueueSimulation)
		self.tab_simulation.button_stop_simulation.clicked.connect(self.stopSimulation)	   
		self.tab_simulation.spinbox_delta_time.valueChanged.connect(self.adjustTotalTime)
		self.tab_simulation.spinbox_time_steps.valueChanged.connect(self.adjustTotalTime)
		self.tab_simulation.spinbox_total_time.valueChanged.connect(self.adjustDeltaTime)
		self.tab_plot.button_update_plot.clicked.connect(self.updatePlot)
		self.tab_analysis.button_calculate_period.clicked.connect(self.calculateOrbitalPeriod)
	
	
	def adjustTotalTime(self):
		self.tab_simulation.spinbox_total_time.setValue(
			self.tab_simulation.spinbox_delta_time.value() * self.tab_simulation.spinbox_time_steps.value()
		)
	
	
	def adjustDeltaTime(self):
		if self.tab_simulation.spinbox_time_steps.value() != 0:
			self.tab_simulation.spinbox_delta_time.setValue(
				self.tab_simulation.spinbox_total_time.value() / self.tab_simulation.spinbox_time_steps.value()
			)
	
	
	def save(self):
		objects = [row[1] for row in self.object_list]
		file_out = """#Name\tPrimary\tMass\tx\ty\tz\tvx\tvy\tvz\n"""
		for elem in objects:
			file_out += (
			elem.getName() + "\t" + 
			elem.getPrimaryName() + "\t" + 
			str(elem.getMass()) + "\t" + 
			str(elem.getX()) + "\t" + str(elem.getY()) + "\t" + str(elem.getZ()) + "\t" +
			str(elem.getVx()) + "\t" + str(elem.getVy()) + "\t" + str(elem.getVz()) + "\n"
		)
			
		file_name = QtGui.QFileDialog.getSaveFileName(
			self, 
			'Save file', 
			"", 
			'Save files (*.dat)', 
			'Save files (*.dat)'
		)[0]
		if file_name != '':
			f = open(os.path.splitext(file_name)[0]+'.dat', 'w+')
			f.write(file_out)
			f.close()
	
	
	def load(self):
		file_name = QtGui.QFileDialog.getOpenFileName(
			self, 
			'Load file', 
			"", 
			'Save files (*.dat)', 
			'Save files (*.dat)'
		)[0]
		if file_name != '':
			f = open(file_name, 'r')
			file_in = f.read()
			f.close()
			
			if file_in.split("\n")[0] == """#Name\tPrimary\tMass\tx\ty\tz\tvx\tvy\tvz""":
				self.deleteAllObjects()
				for line in file_in.split("\n")[1:-1]:
					if line[0] != '#': # comments
						nodes = line.split("\t")
						self.object_list.append(
							[
							QtGui.QTreeWidgetItem(),
							AstronomicalObject(
								nodes[0], 
								float(nodes[2]), 
								nodes[1], 
								float(nodes[3]), 
								float(nodes[4]), 
								float(nodes[5]), 
								float(nodes[6]), 
								float(nodes[7]), 
								float(nodes[8]) )
							]
							)
						self.object_list[-1][0].setText(0, nodes[0])
						if nodes[1] == "no primary":
							self.tab_objects.objects_tree.addTopLevelItem(self.object_list[-1][0])
						else:
							tmp = self.searchTree(
								[self.tab_objects.objects_tree.topLevelItem(i) for i in range(self.tab_objects.objects_tree.topLevelItemCount())], 
								nodes[1]
							)
							if tmp:
								tmp.addChild(self.object_list[-1][0])
							else:
								None
								#This is an error
					   
						self.updatePrimaryList()
			else:
				self._parent.status_msg.setText("Error: invalid file")
		
		
	def deleteSelectedObject(self):
		item_is_top_level = False#workaround; see below...
		
		for item in self.tab_objects.objects_tree.selectedItems():
			nodes = self.getSubtreeNodes(item)
			for i in nodes:
				for elem in range(len(self.object_list)):
					if i is self.object_list[elem][0]:
						self.object_list.pop(elem)
						self.tab_objects.combobox_object_primary.removeItem(elem+1)
						break
					
			for i in [self.tab_objects.objects_tree.topLevelItem(i) for i in range(self.tab_objects.objects_tree.topLevelItemCount())]:
				if i is item:
					item_is_top_level = True
					self.tab_objects.objects_tree.takeTopLevelItem(self.tab_objects.objects_tree.indexOfTopLevelItem(item))
					break
			if item_is_top_level == False:
				parent = self.searchTree([self.tab_objects.objects_tree.itemAt(i,0) for i in range(self.tab_objects.objects_tree.topLevelItemCount())], item.text(0)).parent()
				parent.takeChild(parent.indexOfChild(item))
			
			self.updatePrimaryList()
			
	def deleteAllObjects(self):
		item_is_top_level = False

		for j in range(self.tab_objects.objects_tree.topLevelItemCount()):
			item = self.tab_objects.objects_tree.itemAt(j,0)
			nodes = self.getSubtreeNodes(item)
			for i in nodes:
				for elem in range(len(self.object_list)):
					if i is self.object_list[elem][0]:
						self.object_list.pop(elem)
						self.tab_objects.combobox_object_primary.removeItem(elem+1)
						break
					
			for i in [self.tab_objects.objects_tree.topLevelItem(i) for i in range(self.tab_objects.objects_tree.topLevelItemCount())]:
				if i is item:
					item_is_top_level = True
					self.tab_objects.objects_tree.takeTopLevelItem(self.tab_objects.objects_tree.indexOfTopLevelItem(item))
					break
			if item_is_top_level == False:
				parent = self.searchTree(
					[self.tab_objects.objects_tree.itemAt(i,0) for i in range(self.tab_objects.objects_tree.topLevelItemCount())], 
					item.text(0)
				).parent()
				parent.takeChild(parent.indexOfChild(item))
			
			self.updatePrimaryList()
	
	def getSubtreeNodes(self, tree_widget_item):
		"""
		Returns all QTreeWidgetItems in the subtree rooted at the given node.
		"""
		nodes = []
		nodes.append(tree_widget_item)
		for i in range(tree_widget_item.childCount()):
			nodes.extend(self.getSubtreeNodes(tree_widget_item.child(i)))
		return nodes
		
	
	def addBody(self):
		if self.tab_objects.lineedit_object_name.displayText() != "":
			index = -1
			for elem in range(len(self.object_list)):
				if self.object_list[elem][1].getName() == self.tab_objects.lineedit_object_name.displayText():
					msg = QtGui.QMessageBox(self)
					msg.setText("An object with the same name already exists.\nPlease delete duplicate first.")
					msg.setWindowTitle("Error adding object")
					msg.exec()
					index = -2
			
			if index == -2:
				None
			elif index >= -1:
				if index == -1:
					self.object_list.append(
						[
						QtGui.QTreeWidgetItem(),
						AstronomicalObject(
							self.tab_objects.lineedit_object_name.displayText(), 
							self.tab_objects.spinbox_object_mass.value(), 
							self.tab_objects.combobox_object_primary.currentText(), 
							self.tab_objects.spinbox_x_initial.value(), 
							self.tab_objects.spinbox_y_initial.value(), 
							self.tab_objects.spinbox_z_initial.value(), 
							self.tab_objects.spinbox_vx_initial.value(), 
							self.tab_objects.spinbox_vy_initial.value(), 
							self.tab_objects.spinbox_vz_initial.value() )
						]
						)
				else:
					#this case should never be triggered
					self.object_list[index][1] =  AstronomicalObject(
							self.tab_objects.lineedit_object_name.displayText(), 
							self.tab_objects.spinbox_object_mass.value(), 
							self.tab_objects.combobox_object_primary.currentText(), 
							self.tab_objects.spinbox_x_initial.value(), 
							self.tab_objects.spinbox_y_initial.value(), 
							self.tab_objects.spinbox_z_initial.value(), 
							self.tab_objects.spinbox_vx_initial.value(), 
							self.tab_objects.spinbox_vy_initial.value(), 
							self.tab_objects.spinbox_vz_initial.value() )
				self.object_list[index][0].setText(0, self.tab_objects.lineedit_object_name.displayText())
				if self.tab_objects.combobox_object_primary.currentText() == "no primary":
					self.tab_objects.objects_tree.addTopLevelItem(self.object_list[index][0])
				else:
					tmp = self.searchTree(
						[self.tab_objects.objects_tree.topLevelItem(i) for i in range(self.tab_objects.objects_tree.topLevelItemCount())], 
						self.tab_objects.combobox_object_primary.currentText()
					)
					if tmp:
						tmp.addChild(self.object_list[index][0])
					else:
						None
						#This is an error
				self.updatePrimaryList()
			
			
	def searchTree(self, list_of_items, name):
		"""
		returns the QTreeWidgetItem with name "name"
		"""
		if len(list_of_items) == 0:
			return None
		else:
			items_all = []
			for item in list_of_items:
				items_all.extend(self.getSubtreeNodes(item))
			for i in items_all:
				if i.text(0) == name:
					return i
	
	
	def editObject(self):
		"""
		Displays all attributes of an object in the UI
		"""
		for item in self.tab_objects.objects_tree.selectedItems():
			for elem in range(len(self.object_list)):
				if item is self.object_list[elem][0]:
					tmp = self.object_list[elem][1]
					self.tab_objects.lineedit_object_name.setText(tmp.getName())
					self.tab_objects.spinbox_object_mass.setValue(tmp.getMass())
					self.tab_objects.combobox_object_primary.setCurrentIndex(
						self.tab_objects.combobox_object_primary.findText(tmp.getPrimaryName())
					)
					self.tab_objects.spinbox_x_initial.setValue(tmp.getX())
					self.tab_objects.spinbox_y_initial.setValue(tmp.getY())
					self.tab_objects.spinbox_z_initial.setValue(tmp.getZ())
					self.tab_objects.spinbox_vx_initial.setValue(tmp.getVx())
					self.tab_objects.spinbox_vy_initial.setValue(tmp.getVy())
					self.tab_objects.spinbox_vz_initial.setValue(tmp.getVz())
	 
	 
	def updatePrimaryList(self):
		"""
		Refreshes the list of possible primaries
		"""
		self.tab_objects.combobox_object_primary.clear()
		self.tab_objects.combobox_object_primary.addItem("no primary")
		for elem in range(len(self.object_list)):
			self.tab_objects.combobox_object_primary.addItem(self.object_list[elem][1].getName())
			
			
	def enqueueSimulation(self):
		"""
		start separate thread that performs the simulation 
		"""
		threshold = (
			int(
				self.tab_simulation.spinbox_time_steps.value() / 
				self.tab_simulation.spinbox_skip_n.value()
			) * 
			len(self.object_list) * 3 * 8 * 5
		) #3 = xyz, 8 = Bit->Byte, 5 = safety margin
		
		if (cl.get_platforms()[0].get_devices()[0].extensions.find("cl_khr_fp64") != -1 or
			cl.get_platforms()[0].get_devices()[0].extensions.find("cl_amd_fp64") != -1):
			openCL_ext = True
		else:
			openCL_ext = False
		
		if psutil.virtual_memory().available < threshold:
			self._parent.status_msg.setText("Error: not enough free system memory")
		elif len(self.object_list) > 0 and self.simulation_running == False:
			if openCL_ext == True:
				worker = Thread(
					target=threadedSimulation, 
					args=(
						self.tab_simulation.spinbox_delta_time.value(), 
						int(self.tab_simulation.spinbox_time_steps.value()), 
						[row[1] for row in self.object_list], 
						self.queue_data, 
						self.queue_comm, 
						self.tab_simulation.spinbox_skip_n.value(), 
						self.tab_simulation.checkbox_openCL.isChecked(),
						"first order leapfrog" if (
							self.tab_simulation.combobox_method.currentText() == "first order leapfrog (fast)"
						) else "PEFRL"
					)
				)
				worker.start()
				self.simulation_running = True
				self._parent.status_msg.setText("Running simulation")
				self._parent.progress_bar.show()
			else:
				self._parent.status_msg.setText("Error: no OpenCL device matching specifications found")
	
	
	def stopSimulation(self):
		if self.simulation_running == True:
			if not self.queue_comm.empty():
				self.queue_comm.get()
			try:
				self.queue_comm.put("stop")
			except:
				None
			self.queue_comm.task_done()
	
	
	def checkQueues(self):
		if not self.queue_data.empty():
			self.setPlotData(self.queue_data.get(timeout=0))
			self.queue_data.task_done()
			self.updatePlot()
			self.simulation_running = False
			self._parent.progress_bar.hide()
			self._parent.progress_bar.setValue(0)
			self._parent.status_msg.setText("Ready")
		if not self.queue_comm.empty():
			self._parent.progress_bar.setValue(self.queue_comm.get(timeout=0))
			self.queue_comm.task_done()
	
	
	def updatePlot(self):
		names = self.getPlotData()[0]
		pos = np.copy(self.getPlotData()[2])
		self.plot.clear()
		#rudimentary fix to reset legend--------------------------------
		self.plot.legend.nodes = []
		self.plot.legend.scene().removeItem(self.plot.legend)
		self.plot.addLegend()
		#---------------------------------------------------------------
		
		#get combobox_plot_plane
		if self.tab_plot.combobox_plot_plane.currentText() == "XY":
			plotxindex = 0
			plotyindex = 1
			self.plot.getAxis("bottom").setLabel(text="x", units="m")
			self.plot.getAxis("left").setLabel(text="y", units="m")
		elif self.tab_plot.combobox_plot_plane.currentText() == "YZ":
			plotxindex = 1
			plotyindex = 2
			self.plot.getAxis("bottom").setLabel(text="y", units="m")
			self.plot.getAxis("left").setLabel(text="z", units="m")
		elif self.tab_plot.combobox_plot_plane.currentText() == "XZ":
			plotxindex = 0
			plotyindex = 2
			self.plot.getAxis("bottom").setLabel(text="x", units="m")
			self.plot.getAxis("left").setLabel(text="z", units="m")
			
		#calculate motion relative to selected origin
		if self.tab_plot.combobox_plot_origin.currentText() in names:
			k = names.index(self.tab_plot.combobox_plot_origin.currentText())
			for i in range(len(pos)):
				tmppos = np.copy(pos[i][k])
				for j in range(len(pos[i])):
					pos[i][j] -= tmppos
			
		if len(self.object_list)-1 <= 0:
			corr = 1
		else:
			corr = len(self.object_list)/(len(self.object_list)-1)
		
		for elem in range(len(self.object_list)):
			rgb = givecolor(elem*corr, len(self.object_list))
			tmp = pg.PlotCurveItem(
				pen = pg.mkPen(color=(rgb[0], rgb[1], rgb[2]), width=2), 
				x = np.array([pos[i][elem][plotxindex] for i in range(len(pos))]), 
				y = np.array([pos[i][elem][plotyindex] for i in range(len(pos))]), 
				name = names[elem]
			)
			self.plot.addItem(tmp)
			#if one were to keep and store the reference to eachplot, highlighting etc would be possible
			tmp = None
		self.plot.enableAutoRange(enable = True)
		
		self.tab_plot.updateOrigin(names)
		self.tab_analysis.updateAnalysisComboboxes(names)
		self.tab_analysis.lineedit_orbital_period.setText("")
	
	def calculateOrbitalPeriod(self):
		"""
		calculates the orbital period of a satellite body around another by:
			1) calculating the position over time of the satellite relative to the other body
			2) choose the dimension (X, Y or Z)* where the satellite's position changes 
			   the most over time
			3) perform a FFT of the satellite's position data in that dimension
			4) compare the frequencies/periods associated with the 10 largest peaks in the 
			   FFT-spectrum by calculating the average position mismatch for all possible
			   multiples of that period
			5) the period with the smallest average error is returned as the most likely
			   period
		
		* a more intelligent approach would calculate/approximate the plane in which the
		  object moves and determine the "most suitable" axis for calculating the FFT
		  from a projection of the original data on the plane of motion.
		"""
		
		msg = "unable to determine orbital period"
		
		#disallow calculations if central body and satellite are identical or empty
		if (
			self.tab_analysis.combobox_central_body.currentText() != 
			self.tab_analysis.combobox_satellite_body.currentText() and
			self.tab_analysis.combobox_central_body.count() > 0 and
			self.tab_analysis.combobox_satellite_body.count() > 0
		):
			names = self.getPlotData()[0]
			timestep = self.getPlotData()[1][0] * self.getPlotData()[1][1]
			
			index = names.index(self.tab_analysis.combobox_central_body.currentText())
			pos_central_body = np.copy([ x[index] for x in self.getPlotData()[2] ])
			
			index = names.index(self.tab_analysis.combobox_satellite_body.currentText())
			pos_satellite_body = np.copy([ x[index] for x in self.getPlotData()[2] ])
			
			#calculate motion relative to selected origin
			for i in range(len(pos_central_body)):
				pos_satellite_body[i] -= pos_central_body[i]
			
			#determine position component that changes the most
			comp_max = 0
			mag_max = 0
			for i in range(3):
				tmp = abs(
					max([x[i] for x in pos_satellite_body]) - 
					min([x[i] for x in pos_satellite_body])
				)
				if tmp > mag_max:
					mag_max = tmp
					comp_max = i
			
			pos_satellite_body_comp_max = [x[comp_max] for x in pos_satellite_body]
			
			#FFT
			frequency_values = fftfreq(len(pos_satellite_body_comp_max), d=timestep)
			frequency_magnitude = np.absolute(rfft(pos_satellite_body_comp_max))
			
			#get the 10 most likely candidates for the orbital period 
			max_val_indexes = np.argpartition(frequency_magnitude, -10)[-10:]
			
			#compare errors for each of the 10 candidates
			comp_min = -1
			comp_error = mag_max / 2.0
			for i in max_val_indexes:
				tmp_period = 2.0 / frequency_values[i] / timestep
				if tmp_period <= len(pos_satellite_body) and tmp_period > 0:
					num_periods = int(len(pos_satellite_body) / tmp_period)
					period_indexes = [int(tmp_period * x) for x in list(range(num_periods+1))[1:]]
					if period_indexes[-1] >= len(pos_satellite_body):
						del period_indexes[-1]
					if len(period_indexes) > 0:
						tmp = 0
						for j in period_indexes:
							tmp += np.linalg.norm(np.array(pos_satellite_body[j]) - np.array(pos_satellite_body[0]))
						tmp /= len(period_indexes)
						if tmp < comp_error:
							comp_min = i
							comp_error = tmp
			
			if comp_min > 0:
				period_seconds = 2.0 / frequency_values[comp_min]
				period_days = period_seconds / 86400.0
				period_years = period_days / 365.0
				
				msg = (
					str(period_seconds) + " s ≡ " + 
					str(period_days) + " d ≡ " + 
					str(period_years) + " a"
			)
		
		self.tab_analysis.lineedit_orbital_period.setText(msg)

		
def main():
	app = QtWidgets.QApplication(sys.argv)
	app.setWindowIcon(QtGui.QIcon('icon.png'))
	ex = PantheonMainWindow()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()