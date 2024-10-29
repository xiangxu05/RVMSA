from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow
from PyQt5 import uic
from PyQt5.QtChart import QChartView
class Stats:

    def __init__(self):
        # 从文件中加载UI定义
        self.ui = uic.loadUi("widget.ui")


if __name__ == "__main__":
    app = QApplication([])
    stats = Stats()
    if stats.ui:
        stats.show()
    app.exec_()
