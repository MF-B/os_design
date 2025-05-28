import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QSpinBox, 
                            QGroupBox, QTextEdit, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont

class WorkerSignals(QObject):
    """定义信号类，用于线程和主UI通信"""
    buffer_update = pyqtSignal(str, str, str)
    log_message = pyqtSignal(str)
    data_flow = pyqtSignal(str, str)  # 添加数据流动信号

class DataItem(QLabel):
    """移动的数据项"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(20, 20)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 10px;
            }
        """)

class FlowWidget(QWidget):
    """数据流动显示组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(300)
        self.moving_items = []  # 存储正在移动的数据项
        self.init_ui()
        
    def init_ui(self):
        """初始化UI布局"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # 第一层：生产者
        producer_layout = QHBoxLayout()
        producer_layout.addStretch()
        self.producer_label = QLabel("生产者")
        self.producer_label.setStyleSheet("""
            QLabel {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        self.producer_label.setFixedSize(80, 40)
        self.producer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        producer_layout.addWidget(self.producer_label)
        producer_layout.addStretch()
        layout.addLayout(producer_layout)
        
        # 第二层：缓冲区1
        buffer1_layout = QHBoxLayout()
        buffer1_layout.addStretch()
        self.buffer1_label = QLabel("缓冲区1")
        self.buffer1_label.setStyleSheet("""
            QLabel {
                background-color: #FF9800;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        self.buffer1_label.setFixedSize(80, 40)
        self.buffer1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buffer1_layout.addWidget(self.buffer1_label)
        buffer1_layout.addStretch()
        layout.addLayout(buffer1_layout)
        
        # 第三层：缓冲区2和3
        buffer23_layout = QHBoxLayout()
        buffer23_layout.addStretch()
        
        self.buffer2_label = QLabel("缓冲区2")
        self.buffer2_label.setStyleSheet("""
            QLabel {
                background-color: #9C27B0;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        self.buffer2_label.setFixedSize(80, 40)
        self.buffer2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buffer23_layout.addWidget(self.buffer2_label)
        
        buffer23_layout.addStretch()
        
        self.buffer3_label = QLabel("缓冲区3")
        self.buffer3_label.setStyleSheet("""
            QLabel {
                background-color: #9C27B0;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        self.buffer3_label.setFixedSize(80, 40)
        self.buffer3_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buffer23_layout.addWidget(self.buffer3_label)
        buffer23_layout.addStretch()
        layout.addLayout(buffer23_layout)
        
        # 第四层：消费者
        consumer_layout = QHBoxLayout()
        consumer_layout.addStretch()
        
        self.consumer1_label = QLabel("消费者1")
        self.consumer1_label.setStyleSheet("""
            QLabel {
                background-color: #F44336;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        self.consumer1_label.setFixedSize(80, 40)
        self.consumer1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        consumer_layout.addWidget(self.consumer1_label)
        
        consumer_layout.addStretch()
        
        self.consumer2_label = QLabel("消费者2")
        self.consumer2_label.setStyleSheet("""
            QLabel {
                background-color: #F44336;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        self.consumer2_label.setFixedSize(80, 40)
        self.consumer2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        consumer_layout.addWidget(self.consumer2_label)
        consumer_layout.addStretch()
        layout.addLayout(consumer_layout)
        
        self.setLayout(layout)
        
    def paintEvent(self, event):
        """绘制连接线"""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 设置画笔
        pen = QPen(QColor("#666666"), 2)
        painter.setPen(pen)
        
        # 获取各组件的中心位置
        producer_center = self.producer_label.geometry().center()
        buffer1_center = self.buffer1_label.geometry().center()
        buffer2_center = self.buffer2_label.geometry().center()
        buffer3_center = self.buffer3_label.geometry().center()
        consumer1_center = self.consumer1_label.geometry().center()
        consumer2_center = self.consumer2_label.geometry().center()
        
        # 绘制连接线
        # 生产者 -> 缓冲区1
        painter.drawLine(producer_center.x(), producer_center.y() + 20,
                        buffer1_center.x(), buffer1_center.y() - 20)
        
        # 缓冲区1 -> 缓冲区2
        painter.drawLine(buffer1_center.x() - 20, buffer1_center.y() + 20,
                        buffer2_center.x(), buffer2_center.y() - 20)
        
        # 缓冲区1 -> 缓冲区3
        painter.drawLine(buffer1_center.x() + 20, buffer1_center.y() + 20,
                        buffer3_center.x(), buffer3_center.y() - 20)
        
        # 缓冲区2 -> 消费者1
        painter.drawLine(buffer2_center.x(), buffer2_center.y() + 20,
                        consumer1_center.x(), consumer1_center.y() - 20)
        
        # 缓冲区3 -> 消费者2
        painter.drawLine(buffer3_center.x(), buffer3_center.y() + 20,
                        consumer2_center.x(), consumer2_center.y() - 20)
        
    def animate_data_flow(self, data, flow_type):
        """创建数据流动动画
        flow_type: 'produce', 'move_to_2', 'move_to_3', 'consume_1', 'consume_2'
        """
        data_item = DataItem(str(data), self)
        
        # 根据流动类型确定起点和终点
        if flow_type == 'produce':
            start_pos = self.producer_label.geometry().center()
            end_pos = self.buffer1_label.geometry().center()
        elif flow_type == 'move_to_2':
            start_pos = self.buffer1_label.geometry().center()
            end_pos = self.buffer2_label.geometry().center()
        elif flow_type == 'move_to_3':
            start_pos = self.buffer1_label.geometry().center()
            end_pos = self.buffer3_label.geometry().center()
        elif flow_type == 'consume_1':
            start_pos = self.buffer2_label.geometry().center()
            end_pos = self.consumer1_label.geometry().center()
        elif flow_type == 'consume_2':
            start_pos = self.buffer3_label.geometry().center()
            end_pos = self.consumer2_label.geometry().center()
        else:
            return
            
        # 调整位置使数据项居中
        start_pos.setX(start_pos.x() - 10)
        start_pos.setY(start_pos.y() - 10)
        end_pos.setX(end_pos.x() - 10)
        end_pos.setY(end_pos.y() - 10)
        
        # 设置初始位置
        data_item.move(start_pos)
        data_item.show()
        
        # 创建动画
        animation = QPropertyAnimation(data_item, b"geometry")
        animation.setDuration(1000)  # 1秒动画
        animation.setStartValue(QRect(start_pos.x(), start_pos.y(), 20, 20))
        animation.setEndValue(QRect(end_pos.x(), end_pos.y(), 20, 20))
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # 动画结束后清理
        def cleanup():
            if data_item in self.moving_items:
                self.moving_items.remove(data_item)
            data_item.deleteLater()
            
        animation.finished.connect(cleanup)
        
        # 开始动画
        self.moving_items.append(data_item)
        animation.start()
        
        # 保持动画对象的引用
        data_item.animation = animation

class ProducerConsumerUI(QMainWindow):
    """生产者-消费者系统UI定义"""
    def __init__(self):
        super().__init__()
        
        # 设置窗口
        self.setWindowTitle("生产者-消费者系统")
        self.setMinimumSize(1000, 800)
        
        # 创建主部件和布局
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # 添加控制面板
        control_group = QGroupBox("系统控制")
        control_layout = QHBoxLayout()
        
        # 启动/停止按钮
        self.start_btn = QPushButton("启动系统")
        control_layout.addWidget(self.start_btn)
        
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)
        
        # 添加参数设置面板
        params_group = QGroupBox("参数设置")
        params_layout = QGridLayout()
        
        # 缓冲区大小设置
        params_layout.addWidget(QLabel("缓冲区1大小:"), 0, 0)
        self.buffer1_size = QSpinBox()
        self.buffer1_size.setRange(1, 20)
        self.buffer1_size.setValue(8)
        params_layout.addWidget(self.buffer1_size, 0, 1)
        
        params_layout.addWidget(QLabel("缓冲区2大小:"), 0, 2)
        self.buffer2_size = QSpinBox()
        self.buffer2_size.setRange(1, 20)
        self.buffer2_size.setValue(4)
        params_layout.addWidget(self.buffer2_size, 0, 3)
        
        params_layout.addWidget(QLabel("缓冲区3大小:"), 0, 4)
        self.buffer3_size = QSpinBox()
        self.buffer3_size.setRange(1, 20)
        self.buffer3_size.setValue(4)
        params_layout.addWidget(self.buffer3_size, 0, 5)
        
        # 频率设置
        params_layout.addWidget(QLabel("生产者频率:"), 1, 0)
        self.producer_freq = QSpinBox()
        self.producer_freq.setRange(1, 10)
        self.producer_freq.setValue(2)
        params_layout.addWidget(self.producer_freq, 1, 1)
        
        # 消费者1频率
        params_layout.addWidget(QLabel("消费者1获取频率:"), 1, 2)
        self.c1_get_freq = QSpinBox()
        self.c1_get_freq.setRange(1, 10)
        self.c1_get_freq.setValue(1)
        params_layout.addWidget(self.c1_get_freq, 1, 3)
        
        params_layout.addWidget(QLabel("消费者1移动频率:"), 1, 4)
        self.c1_move_freq = QSpinBox()
        self.c1_move_freq.setRange(1, 10)
        self.c1_move_freq.setValue(2)
        params_layout.addWidget(self.c1_move_freq, 1, 5)
        
        # 消费者2频率
        params_layout.addWidget(QLabel("消费者2获取频率:"), 2, 2)
        self.c2_get_freq = QSpinBox()
        self.c2_get_freq.setRange(1, 10)
        self.c2_get_freq.setValue(1)
        params_layout.addWidget(self.c2_get_freq, 2, 3)
        
        params_layout.addWidget(QLabel("消费者2移动频率:"), 2, 4)
        self.c2_move_freq = QSpinBox()
        self.c2_move_freq.setRange(1, 10)
        self.c2_move_freq.setValue(2)
        params_layout.addWidget(self.c2_move_freq, 2, 5)
        
        params_group.setLayout(params_layout)
        main_layout.addWidget(params_group)
        
        # 添加数据流动可视化
        flow_group = QGroupBox("数据流动可视化")
        flow_layout = QVBoxLayout()
        
        self.flow_widget = FlowWidget()
        flow_layout.addWidget(self.flow_widget)
        
        flow_group.setLayout(flow_layout)
        main_layout.addWidget(flow_group)
        
        # 缓冲区状态显示
        buffer_group = QGroupBox("缓冲区状态")
        buffer_layout = QHBoxLayout()
        
        self.buffer1_display = QTextEdit()
        self.buffer1_display.setReadOnly(True)
        self.buffer1_display.setMaximumHeight(150)
        buffer_layout.addWidget(self.buffer1_display)
        
        self.buffer2_display = QTextEdit()
        self.buffer2_display.setReadOnly(True)
        self.buffer2_display.setMaximumHeight(150)
        buffer_layout.addWidget(self.buffer2_display)
        
        self.buffer3_display = QTextEdit()
        self.buffer3_display.setReadOnly(True)
        self.buffer3_display.setMaximumHeight(150)
        buffer_layout.addWidget(self.buffer3_display)
        
        buffer_group.setLayout(buffer_layout)
        main_layout.addWidget(buffer_group)
        
        # 日志显示
        log_group = QGroupBox("系统日志")
        log_layout = QVBoxLayout()
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(200)
        log_layout.addWidget(self.log_display)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # 设置主部件
        self.setCentralWidget(main_widget)
    
    def update_buffer_display(self, buffer1_str, buffer2_str, buffer3_str):
        """更新缓冲区显示"""
        self.buffer1_display.setText(f"缓冲区1:\n{buffer1_str}")
        self.buffer2_display.setText(f"缓冲区2:\n{buffer2_str}")
        self.buffer3_display.setText(f"缓冲区3:\n{buffer3_str}")
    
    def append_log(self, message):
        """添加日志信息"""
        self.log_display.append(message)
        # 滚动到底部
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum())
    
    def animate_data_flow(self, data, flow_type):
        """触发数据流动动画"""
        self.flow_widget.animate_data_flow(data, flow_type)