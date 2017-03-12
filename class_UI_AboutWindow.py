from PyQt5 import QtGui, QtCore, QtWidgets

class aboutDialog(QtWidgets.QDialog):
	"""
	Class that defines the UI for the 'about' window.
	"""
	def __init__(self, parent=None):
		super(aboutDialog, self).__init__(parent)
		
		self.setGeometry(200, 200, 520, 400)
		self.setMinimumSize(520,300)
		self.setMaximumWidth(520)
		self.setWindowTitle('About')

		self.button_close = QtWidgets.QPushButton(self)
		self.button_close.setText("Close")
		self.button_close.clicked.connect(self.close)

		self.scrollarea_license = QtWidgets.QScrollArea(self)
		self.scrollarea_license.setWidgetResizable(True)
		self.scrollarea_license.setWidget(QtWidgets.QLabel(open("Licenses.txt", 'r').read()))

		self.layout_license = QtWidgets.QVBoxLayout(self)
		self.layout_license.addWidget(self.scrollarea_license)		
		self.layout_license.addWidget(self.button_close)