import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget
from PyQt6.QtCore import QTimer, QPropertyAnimation, QPoint


class Buffer(QWidget):
    def __init__(self, name):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel(name)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.items = []

    def add_item(self, item):
        self.items.append(item)
        label = QLabel(item)
        self.layout.addWidget(label)

    def remove_item(self):
        if self.items:
            item = self.items.pop(0)
            self.layout.takeAt(1).widget().deleteLater()
            return item
        return None


class AnimationDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("生产者-消费者动画")

        # 主布局
        main_layout = QVBoxLayout()

        # 三个缓冲区
        self.producer = Buffer("生产者")
        self.consumer1 = Buffer("消费者1")
        self.consumer2 = Buffer("消费者2")

        buffers_layout = QHBoxLayout()
        buffers_layout.addWidget(self.producer)
        buffers_layout.addWidget(self.consumer1)
        buffers_layout.addWidget(self.consumer2)
        main_layout.addLayout(buffers_layout)

        # 控制按钮
        control_layout = QHBoxLayout()
        self.put_button = QPushButton("PUT")
        self.put_button.clicked.connect(self.put_data)
        self.move_button1 = QPushButton("MOVE to 消费者1")
        self.move_button1.clicked.connect(lambda: self.move_data(self.consumer1))
        self.move_button2 = QPushButton("MOVE to 消费者2")
        self.move_button2.clicked.connect(lambda: self.move_data(self.consumer2))
        self.get_button1 = QPushButton("GET 消费者1")
        self.get_button1.clicked.connect(lambda: self.get_data(self.consumer1))
        self.get_button2 = QPushButton("GET 消费者2")
        self.get_button2.clicked.connect(lambda: self.get_data(self.consumer2))

        control_layout.addWidget(self.put_button)
        control_layout.addWidget(self.move_button1)
        control_layout.addWidget(self.move_button2)
        control_layout.addWidget(self.get_button1)
        control_layout.addWidget(self.get_button2)
        main_layout.addLayout(control_layout)

        # 设置主窗口
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def put_data(self):
        item = str(random.randint(1, 100))
        self.producer.add_item(item)

    def move_data(self, consumer):
        item = self.producer.remove_item()
        if item:
            consumer.add_item(item)
            self.animate_transfer(self.producer, consumer)

    def get_data(self, consumer):
        consumer.remove_item()

    def animate_transfer(self, source, target):
        animation = QPropertyAnimation(source, b'pos')
        animation.setDuration(500)
        animation.setStartValue(source.pos())
        animation.setEndValue(target.pos())
        animation.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnimationDemo()
    window.show()
    sys.exit(app.exec())
