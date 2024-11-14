# coding:UTF-8
"""
    测试文件
    Test file
"""
import time
import datetime
import platform
import struct
import chs.lib.device_model as deviceModel
from chs.lib.data_processor.roles.jy901s_dataProcessor import JY901SDataProcessor
from chs.lib.protocol_resolver.roles.wit_protocol_resolver import WitProtocolResolver
import sys
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
accZ_world_values = []
window_start_time = time.time()  # 初始化为当前时间
window_duration = 0.001
welcome = """

"""
_writeF = None                    #写文件  Write file
_IsWriteF = False                 #写文件标识    Write file identification

# 用于存储竖直方向的加速度数据
accZ_world_values = []  # 存储每个时间窗口内的竖直加速度数据
window_start_time = time.time()  # 记录当前时间窗口的开始时间
output_frequency = 1  # 每收集4个数据点输出一次RMSVA

def calculate_rmsva(acc_values):
    """
    计算竖直加速度均方根值 (RMSVA)
    :param acc_values: 竖直加速度值列表
    :return: RMSVA 值
    """

    if len(accZ_world_values) == 0:
        return 0  # 如果没有数据，返回0
    elif len(accZ_world_values) == 1:
        return accZ_world_values[0]  # 如果只有一个数据点，直接返回该值
    return np.sqrt(np.mean(np.square(acc_values)))

def readConfig(device):
    """
    读取配置信息示例    Example of reading configuration information
    :param device: 设备模型 Device model
    :return:
    """
    tVals = device.readReg(0x02,3)  #读取数据内容、回传速率、通讯速率   Read data content, return rate, communication rate
    if (len(tVals)>0):
        print("返回结果：" + str(tVals))
    else:
        print("无返回")
    tVals = device.readReg(0x23,2)  #读取安装方向、算法  Read the installation direction and algorithm
    if (len(tVals)>0):
        print("返回结果：" + str(tVals))
    else:
        print("无返回")

import numpy as np

def quaternion_to_matrix(q1, q2, q3, q4):
    """
    将四元数转换为旋转矩阵
    :param q1, q2, q3, q4: 四元数的分量
    :return: 旋转矩阵
    """
    return np.array([
        [1 - 2 * (q3 ** 2 + q4 ** 2), 2 * (q2 * q3 - q1 * q4), 2 * (q2 * q4 + q1 * q3)],
        [2 * (q2 * q3 + q1 * q4), 1 - 2 * (q2 ** 2 + q4 ** 2), 2 * (q3 * q4 - q1 * q2)],
        [2 * (q2 * q4 - q1 * q3), 2 * (q3 * q4 + q1 * q2), 1 - 2 * (q2 ** 2 + q3 ** 2)]
    ])

def convert_acc_to_world(accX, accY, accZ, q1, q2, q3, q4):
    """
    将设备坐标系下的加速度转换到世界坐标系
    :param accX, accY, accZ: 设备坐标系下的加速度
    :param q1, q2, q3, q4: 四元数分量
    :return: 世界坐标系下的加速度
    """
    acc = np.array([accX, accY, accZ])
    rotation_matrix = quaternion_to_matrix(q1, q2, q3, q4)
    acc_world = np.dot(rotation_matrix, acc)
    return acc_world[0], acc_world[1], acc_world[2]


def setConfig(device):
    """
    设置配置信息示例    Example setting configuration information
    :param device: 设备模型 Device model
    :return:
    """
    device.unlock()                # 解锁 unlock
    time.sleep(0.1)                # 休眠100毫秒    Sleep 100ms
    device.writeReg(0x03, 6)       # 设置回传速率为10HZ    Set the transmission back rate to 10HZ
    time.sleep(0.1)                # 休眠100毫秒    Sleep 100ms
    device.writeReg(0x23, 0)       # 设置安装方向:水平、垂直   Set the installation direction: horizontal and vertical
    time.sleep(0.1)                # 休眠100毫秒    Sleep 100ms
    device.writeReg(0x24, 0)       # 设置安装方向:九轴、六轴   Set the installation direction: nine axis, six axis
    time.sleep(0.1)                # 休眠100毫秒    Sleep 100ms
    device.save()                  # 保存 Save

def AccelerationCalibration(device):
    """
    加计校准    Acceleration calibration
    :param device: 设备模型 Device model
    :return:
    """
    device.AccelerationCalibration()                 # Acceleration calibration
    print("加计校准结束")

def FiledCalibration(device):
    """
    磁场校准    Magnetic field calibration
    :param device: 设备模型 Device model
    :return:
    """
    device.BeginFiledCalibration()                   # 开始磁场校准   Starting field calibration
    if input("请分别绕XYZ轴慢速转动一圈，三轴转圈完成后，结束校准（Y/N)？").lower()=="y":
        device.EndFiledCalibration()                 # 结束磁场校准   End field calibration
        print("结束磁场校准")

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super(PlotCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.ax.set_title('Real-Time RMSVA')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('RMSVA')
        self.x_data = []
        self.y_data = []

    def plot(self, x, y):
        self.ax.clear()
        self.ax.set_title('Real-Time RMSVA')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('RMSVA')
        self.ax.plot(x, y, 'r-', label='RMSVA')
        self.ax.legend()
        self.draw()

from scipy.interpolate import CubicSpline  # 引入 CubicSpline
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self, device_model):
        super().__init__()
        self.device_model = device_model
        self.setWindowTitle("RMSVA 实时折线图")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.canvas = PlotCanvas(self, width=5, height=4)
        self.layout.addWidget(self.canvas)

        self.timer = QTimer(self)
        self.timer.setInterval(100)  # 每 0.2 秒更新一次
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

        self.start_time = time.time()
        self.x_data = []
        self.y_data = []

    def update_plot(self):
        current_time = time.time() - self.start_time
        rmsva = onUpdate(self.device_model)  # 调用 onUpdate 获取 RMSVA

        if rmsva is not None:
            self.x_data.append(current_time)
            self.y_data.append(rmsva)

            # 保持数据长度不超过100个数据点
            if len(self.x_data) > 100:
                self.x_data.pop(0)
                self.y_data.pop(0)

            # 确保有足够的数据点进行样条插值
            if len(self.x_data) > 2 and len(self.y_data) > 2:
                # 使用样条插值使曲线更加平滑
                x_smooth = np.linspace(min(self.x_data), max(self.x_data), 500)  # 创建更多的 x 点
                spline = CubicSpline(self.x_data, self.y_data)  # 样条插值
                y_smooth = spline(x_smooth)  # 获取平滑的 y 值

                # 绘图
                self.canvas.ax.clear()
                self.canvas.ax.plot(x_smooth, y_smooth, 'r-', label='RMSVA', linewidth=1, alpha=0.85)

                # 设置横坐标范围完整输出
                self.canvas.ax.set_xlim(min(self.x_data), max(self.x_data))

                # 设置纵坐标范围为0到2
                self.canvas.ax.set_ylim(0, 2)

                # 扩大0.5-1.5区间的可视化，调整刻度比例
                self.canvas.ax.set_yscale('linear')
                self.canvas.ax.set_yticks([0, 0.25, 0.5, 1, 1.5, 2])
                self.canvas.ax.grid(True)  # 添加网格线来帮助观察

                # 重新绘制图表
                self.canvas.ax.legend()
                self.canvas.draw()
            else:
                print("数据不足以进行插值")
        else:
            print("RMSVA 为 None，未更新图表")



def onUpdate(deviceModel):
    """
    数据更新事件  Data update event
    :param deviceModel: 设备模型    Device model
    :return:
    """
    global accZ_world_values, window_start_time, window_duration

    # 提取设备坐标系下的加速度数据
    accX = deviceModel.getDeviceData("accX")
    accY = deviceModel.getDeviceData("accY")
    accZ = deviceModel.getDeviceData("accZ")

    # 获取四元数数据
    q1 = deviceModel.getDeviceData("q1")
    q2 = deviceModel.getDeviceData("q2")
    q3 = deviceModel.getDeviceData("q3")
    q4 = deviceModel.getDeviceData("q4")

    # 检查加速度数据和四元数数据是否有效
    if accX is None or accY is None or accZ is None or q1 is None or q2 is None or q3 is None or q4 is None:
        print("未能获取有效的数据")
        return None

    # 将加速度转换到世界坐标系
    acc_worldX, acc_worldY, acc_worldZ = convert_acc_to_world(accX, accY, accZ, q1, q2, q3, q4)

    # 将竖直方向的加速度 (Z 轴) 添加到列表中
    accZ_world_values.append(acc_worldZ)

    # 初始化 rmsva 以确保它始终有一个值
    rmsva = 1

    # 当前时间
    current_time = time.time()

    # 每5秒计算一次 RMSVA
    if current_time - window_start_time >= window_duration:
        if len(accZ_world_values) > 0:
            # 计算竖直加速度均方根值 (RMSVA)
            rmsva = calculate_rmsva(accZ_world_values)
        else:
            rmsva = 1  # 如果没有数据，RMSVA 为 0

        #输出加速度数据和 RMSVA
        # print("芯片时间:" + str(deviceModel.getDeviceData("Chiptime"))
        #       , " 加速度：" + str(accX) + "," + str(accY) + "," + str(accZ)
        #       , " 世界坐标系加速度:", round(acc_worldX, 4), round(acc_worldY, 4), round(acc_worldZ, 4)
        #       , " 竖直加速度均方根值 (RMSVA):", round(rmsva, 4))

        # 清空竖直加速度列表，重新开始新的时间窗口
        accZ_world_values = []
        window_start_time = current_time

    # rmsva = rmsva*9.81-9.81
    # 返回 RMSVA，供其他函数使用（如实时图表更新）
    return rmsva,deviceModel.getDeviceData("lon"),deviceModel.getDeviceData("lat"),deviceModel.getDeviceData("Speed")
        # print("芯片时间:" + str(deviceModel.getDeviceData("Chiptime"))
        #     , " 加速度：" + str(accX) + "," + str(accY) + "," + str(accZ)
        #     , " 世界坐标系加速度:", round(acc_worldX, 4), round(acc_worldY, 4), round(acc_worldZ, 4)
        #     , " 竖直加速度均方根值 (RMSVA):", round(rmsva, 4))
        #     , " 温度:" + str(deviceModel.getDeviceData("temperature"))
        #     , " 角速度:" + str(deviceModel.getDeviceData("gyroX")) +","+ str(deviceModel.getDeviceData("gyroY")) +","+ str(deviceModel.getDeviceData("gyroZ"))
        #     , " 角度:" + str(deviceModel.getDeviceData("angleX")) +","+ str(deviceModel.getDeviceData("angleY")) +","+ str(deviceModel.getDeviceData("angleZ"))
        #     , " 磁场:" + str(deviceModel.getDeviceData("magX")) +","+ str(deviceModel.getDeviceData("magY"))+","+ str(deviceModel.getDeviceData("magZ"))
        #     , " 经度:" + str(deviceModel.getDeviceData("lon")) + " 纬度:" + str(deviceModel.getDeviceData("lat"))
        #     , " 航向角:" + str(deviceModel.getDeviceData("Yaw")) + " 地速:" + str(deviceModel.getDeviceData("Speed"))
        #     , " 四元素:" + str(deviceModel.getDeviceData("q1")) + "," + str(deviceModel.getDeviceData("q2")) + "," + str(deviceModel.getDeviceData("q3"))+ "," + str(deviceModel.getDeviceData("q4"))


    # if (_IsWriteF):    #记录数据    Record data
    #     Tempstr = " " + str(deviceModel.getDeviceData("Chiptime"))
    #     Tempstr += "\t"+str(deviceModel.getDeviceData("accX")) + "\t"+str(deviceModel.getDeviceData("accY"))+"\t"+ str(deviceModel.getDeviceData("accZ"))
        # Tempstr += "\t" + str(deviceModel.getDeviceData("gyroX")) +"\t"+ str(deviceModel.getDeviceData("gyroY")) +"\t"+ str(deviceModel.getDeviceData("gyroZ"))
        # Tempstr += "\t" + str(deviceModel.getDeviceData("angleX")) +"\t" + str(deviceModel.getDeviceData("angleY")) +"\t"+ str(deviceModel.getDeviceData("angleZ"))
        # Tempstr += "\t" + str(deviceModel.getDeviceData("temperature"))
        # Tempstr += "\t" + str(deviceModel.getDeviceData("magX")) +"\t" + str(deviceModel.getDeviceData("magY")) +"\t"+ str(deviceModel.getDeviceData("magZ"))
        # Tempstr += "\t" + str(deviceModel.getDeviceData("lon")) + "\t" + str(deviceModel.getDeviceData("lat"))
        # Tempstr += "\t" + str(deviceModel.getDeviceData("Yaw")) + "\t" + str(deviceModel.getDeviceData("Speed"))
        # Tempstr += "\t" + str(deviceModel.getDeviceData("q1")) + "\t" + str(deviceModel.getDeviceData("q2"))
        # Tempstr += "\t" + str(deviceModel.getDeviceData("q3")) + "\t" + str(deviceModel.getDeviceData("q4"))
        # Tempstr += "\t" + str(acc_worldX) + "\t" + str(acc_worldY) + "\t" + str(acc_worldZ) # 世界坐标系加速度
        # Tempstr += "\r\n"
        # _writeF.write(Tempstr)

def startRecord():
    """
    开始记录数据  Start recording data
    :return:
    """
    global _writeF
    global _IsWriteF
    _writeF = open(str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + ".txt", "w")    #新建一个文件
    _IsWriteF = True                                                                        #标记写入标识
    Tempstr = "Chiptime"
    Tempstr +=  "\tax(g)\tay(g)\taz(g)"
    Tempstr += "\twx(deg/s)\twy(deg/s)\twz(deg/s)"
    Tempstr += "\tAngleX(deg)\tAngleY(deg)\tAngleZ(deg)"
    Tempstr += "\tT(°)"
    Tempstr += "\tmagx\tmagy\tmagz"
    Tempstr += "\tlon\tlat"
    Tempstr += "\tYaw\tSpeed"
    Tempstr += "\tq1\tq2\tq3\tq4"
    Tempstr += "\r\n"
    _writeF.write(Tempstr)
    print("开始记录数据")

def endRecord():
    """
    结束记录数据  End record data
    :return:
    """
    global _writeF
    global _IsWriteF
    _IsWriteF = False             # 标记不可写入标识    Tag cannot write the identity
    _writeF.close()               #关闭文件 Close file
    print("结束记录数据")

if __name__ == '__main__':
    print(welcome)
    app = QApplication(sys.argv)
    """
    初始化一个设备模型   Initialize a device model
    """
    device = deviceModel.DeviceModel(
        "我的JY901",
        WitProtocolResolver(),
        JY901SDataProcessor(),
        "51_0"
    )


    if (platform.system().lower() == 'linux'):
        device.serialConfig.portName = "/dev/ttyUSB0"  # 设置串口   Set serial port
    else:
        device.serialConfig.portName = "COM6"  # 设置串口   Set serial port
    device.serialConfig.baud = 9600  # 设置波特率  Set baud rate
    device.openDevice()  # 打开串口   Open serial port
    readConfig(device)  # 读取配置信息 Read configuration information
    device.dataProcessor.onVarChanged.append(onUpdate)  # 数据更新事件 Data update event


    main_window = MainWindow(device)
    main_window.show()
    sys.exit(app.exec_())
