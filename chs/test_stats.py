from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMessageBox

class Stats:
    def __init__(self):
        # 从文件中加载UI定义
        self.ui = uic.loadUi("stats.ui")

        # 连接按钮的点击事件
        self.ui.button.clicked.connect(self.handleCalc)

    def handleCalc(self):
        info = self.ui.textedit.toPlainText()  # 确保引用正确的文本编辑框

        # 薪资20000 以上 和 以下 的人员名单
        salary_above_20k = ''
        salary_below_20k = ''
        for line in info.splitlines():
            if not line.strip():
                continue
            parts = line.split(' ')
            # 去掉列表中的空字符串内容
            parts = [p for p in parts if p]
            if len(parts) < 3:  # 确保有足够的部分
                continue
            name, salary, age = parts
            if int(salary) >= 20000:
                salary_above_20k += name + '\n'
            else:
                salary_below_20k += name + '\n'

        # 显示统计结果
        QMessageBox.about(self.ui,  # 使用 self.ui 而不是 self.window
                          '统计结果',
                          f'''薪资20000 以上的有：\n{salary_above_20k}
                            \n薪资20000 以下的有：\n{salary_below_20k}'''
                          )

app = QApplication([])
stats = Stats()
stats.ui.show()
app.exec_()