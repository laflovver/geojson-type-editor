from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Create main layout
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setObjectName("main_layout")
        
        # Create top toolbar
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        
        # Create buttons
        self.load_btn = QtWidgets.QPushButton()
        self.load_btn.setText("Load GeoJSON")
        self.load_btn.setObjectName("load_btn")
        
        self.mts_btn = QtWidgets.QPushButton()
        self.mts_btn.setText("MTS Integration")
        self.mts_btn.setObjectName("mts_btn")
        
        self.toggle_btn = QtWidgets.QPushButton()
        self.toggle_btn.setText("Toggle Table")
        self.toggle_btn.setObjectName("toggle_btn")
        
        # Add buttons to toolbar
        self.toolbar.addWidget(self.load_btn)
        self.toolbar.addWidget(self.mts_btn)
        self.toolbar.addWidget(self.toggle_btn)
        
        self.main_layout.addWidget(self.toolbar)
        
        # Create split view
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        
        # Left side - JSON editor
        self.json_widget = QtWidgets.QWidget()
        self.json_layout = QtWidgets.QVBoxLayout(self.json_widget)
        self.json_layout.setContentsMargins(0, 0, 0, 0)
        self.json_editor = QtWidgets.QTextEdit()
        self.json_editor.setFont(QtGui.QFont('Roboto Mono', 12))
        self.json_layout.addWidget(self.json_editor)
        self.splitter.addWidget(self.json_widget)
        
        # Right side - Table view
        self.table_widget = QtWidgets.QWidget()
        self.table_layout = QtWidgets.QVBoxLayout(self.table_widget)
        self.table_layout.setContentsMargins(0, 0, 0, 0)
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Property", "Value"])
        self.table.setVisible(False)
        self.table_layout.addWidget(self.table)
        self.splitter.addWidget(self.table_widget)
        
        self.main_layout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Create status bar
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        # Create log area
        self.log_widget = QtWidgets.QWidget()
        self.log_layout = QtWidgets.QVBoxLayout(self.log_widget)
        self.log_layout.setContentsMargins(0, 0, 0, 0)
        self.log = QtWidgets.QTextEdit()
        self.log.setFont(QtGui.QFont('Roboto Mono', 10))
        self.log.setReadOnly(True)
        self.log_layout.addWidget(self.log)
        self.main_layout.addWidget(self.log_widget)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "GeoJSON Type Editor"))
