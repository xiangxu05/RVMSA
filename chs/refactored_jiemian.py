from PyQt5 import QtWidgets, QtCore, QtMultimedia, QtMultimediaWidgets
import sys


class Ui_Widget(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 800)

        self.central_widget = QtWidgets.QWidget(MainWindow)
        self.central_widget.setObjectName("central_widget")
        MainWindow.setCentralWidget(self.central_widget)

        # Main Layout
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(15)
        self.main_layout.setObjectName("main_layout")

        self.setupServerSection()
        self.setupDeviceSection()
        self.setupFileSection()
        self.setupControlButtons()
        self.setupLocationInfo()
        self.setupVisualizationSection()

        # Camera Setup
        self.camera = None
        self.viewfinder = None

    def setupServerSection(self):
        """Set up server connection related UI components."""
        self.server_groupbox = QtWidgets.QGroupBox("Server Settings", self.central_widget)
        self.server_layout = QtWidgets.QHBoxLayout(self.server_groupbox)
        self.server_layout.setContentsMargins(10, 10, 10, 10)
        self.server_layout.setSpacing(10)
        self.server_layout.setObjectName("server_layout")

        # Server Address Section
        self.label_server_ip = QtWidgets.QLabel("Server IP Address", self.server_groupbox)
        self.server_layout.addWidget(self.label_server_ip)
        self.server_ip_input = QtWidgets.QLineEdit(self.server_groupbox)
        self.server_ip_input.setText("192.168.4.1")
        self.server_layout.addWidget(self.server_ip_input)

        # Server Port Section
        self.label_port = QtWidgets.QLabel("Port", self.server_groupbox)
        self.server_layout.addWidget(self.label_port)
        self.server_port_input = QtWidgets.QLineEdit(self.server_groupbox)
        self.server_port_input.setText("8899")
        self.server_layout.addWidget(self.server_port_input)

        self.main_layout.addWidget(self.server_groupbox)

    def setupDeviceSection(self):
        """Set up device connection related UI components."""
        self.device_groupbox = QtWidgets.QGroupBox("Device Settings", self.central_widget)
        self.device_layout = QtWidgets.QHBoxLayout(self.device_groupbox)
        self.device_layout.setContentsMargins(10, 10, 10, 10)
        self.device_layout.setSpacing(10)
        self.device_layout.setObjectName("device_layout")

        # Device IP and Port
        self.label_device_ip = QtWidgets.QLabel("Device IP Address", self.device_groupbox)
        self.device_layout.addWidget(self.label_device_ip)
        self.device_ip_input = QtWidgets.QLineEdit(self.device_groupbox)
        self.device_ip_input.setText("192.168.4.2")
        self.device_layout.addWidget(self.device_ip_input)

        self.label_device_port = QtWidgets.QLabel("Port", self.device_groupbox)
        self.device_layout.addWidget(self.label_device_port)
        self.device_port_input = QtWidgets.QLineEdit(self.device_groupbox)
        self.device_port_input.setText("8899")
        self.device_layout.addWidget(self.device_port_input)

        self.main_layout.addWidget(self.device_groupbox)

    def setupFileSection(self):
        """Set up file selection UI components."""
        self.file_groupbox = QtWidgets.QGroupBox("File Selection", self.central_widget)
        self.file_layout = QtWidgets.QHBoxLayout(self.file_groupbox)
        self.file_layout.setContentsMargins(10, 10, 10, 10)
        self.file_layout.setSpacing(10)
        self.file_layout.setObjectName("file_layout")

        self.label_file_path = QtWidgets.QLabel("File Path", self.file_groupbox)
        self.file_layout.addWidget(self.label_file_path)
        self.file_path_input = QtWidgets.QLineEdit(self.file_groupbox)
        self.file_layout.addWidget(self.file_path_input)
        self.browse_button = QtWidgets.QPushButton("Browse", self.file_groupbox)
        self.file_layout.addWidget(self.browse_button)

        self.main_layout.addWidget(self.file_groupbox)

    def setupControlButtons(self):
        """Set up control buttons."""
        self.control_groupbox = QtWidgets.QGroupBox("Controls", self.central_widget)
        self.control_layout = QtWidgets.QHBoxLayout(self.control_groupbox)
        self.control_layout.setContentsMargins(10, 10, 10, 10)
        self.control_layout.setSpacing(10)
        self.control_layout.setObjectName("control_layout")

        self.start_button = QtWidgets.QPushButton("Start Detection", self.control_groupbox)
        self.start_button.clicked.connect(self.start_camera)
        self.control_layout.addWidget(self.start_button)

        self.stop_button = QtWidgets.QPushButton("Stop Detection", self.control_groupbox)
        self.stop_button.clicked.connect(self.stop_camera)
        self.control_layout.addWidget(self.stop_button)

        self.clear_button = QtWidgets.QPushButton("Clear Data", self.control_groupbox)
        self.control_layout.addWidget(self.clear_button)

        self.main_layout.addWidget(self.control_groupbox)

    def setupLocationInfo(self):
        """Set up location information display."""
        self.location_groupbox = QtWidgets.QGroupBox("Location Information", self.central_widget)
        self.location_layout = QtWidgets.QGridLayout(self.location_groupbox)
        self.location_layout.setContentsMargins(10, 10, 10, 10)
        self.location_layout.setSpacing(10)
        self.location_layout.setObjectName("location_layout")

        self.label_longitude = QtWidgets.QLabel("Longitude", self.location_groupbox)
        self.location_layout.addWidget(self.label_longitude, 0, 0)
        self.longitude_value = QtWidgets.QLabel("0.0", self.location_groupbox)
        self.location_layout.addWidget(self.longitude_value, 0, 1)

        self.label_latitude = QtWidgets.QLabel("Latitude", self.location_groupbox)
        self.location_layout.addWidget(self.label_latitude, 1, 0)
        self.latitude_value = QtWidgets.QLabel("0.0", self.location_groupbox)
        self.location_layout.addWidget(self.latitude_value, 1, 1)

        self.main_layout.addWidget(self.location_groupbox)

    def setupVisualizationSection(self):
        """Set up visualization related components."""
        self.visualization_groupbox = QtWidgets.QGroupBox("Visualization", self.central_widget)
        self.visualization_layout = QtWidgets.QGridLayout(self.visualization_groupbox)
        self.visualization_layout.setContentsMargins(10, 10, 10, 10)
        self.visualization_layout.setSpacing(10)
        self.visualization_layout.setObjectName("visualization_layout")

        # Video Stream Section
        self.viewfinder = QtMultimediaWidgets.QCameraViewfinder(self.visualization_groupbox)
        self.viewfinder.setObjectName("viewfinder")
        self.visualization_layout.addWidget(self.viewfinder, 0, 0, 1, 2)

        # Placeholder for Chart Section
        self.chart_placeholder = QtWidgets.QLabel("Chart Area (for line chart)", self.visualization_groupbox)
        self.chart_placeholder.setAlignment(QtCore.Qt.AlignCenter)
        self.visualization_layout.addWidget(self.chart_placeholder, 1, 0, 1, 2)

        self.main_layout.addWidget(self.visualization_groupbox)

    def start_camera(self):
        """Start the camera using QCamera."""
        self.camera = QtMultimedia.QCamera()
        self.camera.setViewfinder(self.viewfinder)
        self.camera.start()

    def stop_camera(self):
        """Stop the camera."""
        if self.camera:
            self.camera.stop()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = Ui_Widget()
    ui.setupUi(main_window)
    main_window.show()
    sys.exit(app.exec_())
