import torch
from PIL import Image
from pathlib import Path
import pathlib
import sys
import os
import torchvision.transforms as T
# 修复路径问题
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

class CustomYOLO:
    def __init__(self, model_path: str, input_size: tuple = (224, 224)):
        """
        初始化自定义的 YOLO 类

        :param model_path: 加载的模型路径
        :param input_size: 输入图像的目标尺寸，默认为(224, 224)
        """
        #获取当前路径
        FILE = Path(__file__).resolve()
        self.ROOT = FILE.parents[0]  # YOLOv5 root directory
        if str(self.ROOT) not in sys.path:
            sys.path.append(str(self.ROOT))  # add ROOT to PATH
        self.ROOT = Path(os.path.relpath(self.ROOT, Path.cwd()))  # relative

        # 模型路径
        path = Path(str(self.ROOT) + model_path)
        print(f"加载模型路径: {path}")

        # 加载模型，强制重新加载
        self.model = torch.hub.load(str(self.ROOT) + '/yolov5', 'custom', path=str(path), source='local')
        self.model.eval()  # 设置为推理模式

        # 输入图像的目标尺寸
        self.input_size = input_size

        # 定义预处理变换
        self.transform = T.Compose([
            T.Resize(self.input_size),  # 调整图像大小
            T.ToTensor(),  # 转换为 Tensor 格式
        ])
    def predict(self, img_path: str):
        """
        根据图片路径进行推理

        :param img_path: 输入图片的路径
        :return: 预测结果（包括类别、框坐标和置信度）
        """
        # 读取图片
        try:
            img = Image.open(str(self.ROOT)+'/'+img_path).convert('RGB')
        except Exception as e:
            print(f"Error: Unable to open image {img_path}. Error details: {e}")
            return 0,0

        # 进行图片预处理
        img_tensor = self.transform(img).unsqueeze(0)  # 增加 batch 维度

        # 推理
        with torch.no_grad():  # 禁用梯度计算
            results = self.model(img_tensor)

        # 处理结果
        predictions = results[0]

        # 找到最大概率对应的类别
        predicted_class = torch.argmax(predictions).item()  # 获取类别的索引
        predicted_prob = torch.softmax(predictions, dim=0)[predicted_class].item()  # 获取该类别的概率

        # 获取类别名称
        class_names = self.model.names
        predicted_label = class_names[predicted_class]  # 获取预测的类别名称

        return predicted_label, predicted_prob


if __name__ == "__main__":
    # 模型路径
    model_path = '/best-cls.pt'

    # 初始化自定义的 YOLO 类
    yolo = CustomYOLO(model_path=model_path, input_size=(224, 224))

    # 图片路径
    img_path = '20241107_140412_528.png'

    # 获取预测结果
    results = yolo.predict(img_path)

    # 打印预测结果
    print(results)