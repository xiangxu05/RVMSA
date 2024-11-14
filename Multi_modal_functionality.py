import os
import csv
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from datetime import datetime

class DataStorageThread(QThread):
    saveCompleted = pyqtSignal(str)
    receiveData = pyqtSignal(float, float, float, QImage)  # 新增信号

    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath

        # 连接信号到处理函数
        self.receiveData.connect(self.handle_receive_data)

    def run(self):
        print("Thread started, waiting for data...")  # 启动时打印信息
        self.exec_()  # 启动事件循环，等待信号

    def handle_receive_data(self, rmsva, lon, lat, image):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S_")+ f".{datetime.now().microsecond // 1000:03d}"
        try:
            self.data_storage(current_time, rmsva, lon, lat, image)
            self.saveCompleted.emit("Data saved successfully.")
        except Exception as e:
            self.saveCompleted.emit(f"Error: {e}")

    def data_storage(self, current_time, rmsva, lon, lat, image):
        try:
            # 检查文件路径是否有效
            directory = os.path.dirname(self.filepath)
            if not os.path.exists(directory):
                print(f"Directory does not exist: {directory}")
                return

            # 获取 CSV 文件的名字（不带扩展名）用于创建图像文件夹
            csv_name = os.path.splitext(os.path.basename(self.filepath))[0]
            image_folder = os.path.join(directory, f"{csv_name}_file_path")
            os.makedirs(image_folder, exist_ok=True)

            # 以当前时间戳命名图像
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")+ f"{datetime.now().microsecond // 1000:03d}"
            image_path = os.path.join(image_folder, f"{timestamp}.png")

            # 保存图像到指定路径
            image.save(image_path, format='PNG')

            # 准备相对路径用于 CSV 文件
            relative_image_path = os.path.relpath(image_path, directory)

            # 准备数据行
            data_row = [timestamp, rmsva, lon, lat, relative_image_path]  # 将相对路径添加到数据行中
            # print(data_row)

            # 打开文件进行追加，若文件不存在会创建
            with open(self.filepath, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(data_row)

            # print(f"Image saved at: {image_path}")

        except Exception as e:
            print(f"Error saving data: {e}")