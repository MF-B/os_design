import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QSpinBox, 
                            QGroupBox, QTextEdit, QGridLayout, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPropertyAnimation, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

class DataFlowWidget(QFrame):
    """数据流动可视化小部件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(60)
        self.setFrameShape(QFrame.Shape.Box)
        self.setAutoFillBackground(True)
        
        # 流动的数据项
        self.flow_items = []
        
        # 设置背景颜色
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(240, 240, 240))
        self.setPalette(palette)
        
        # 创建动画计时器
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animations)
        self.animation_timer.start(50)  # 20 FPS
    
    def add_data_item(self, data, direction='right'):
        """添加一个数据项并开始动画"""
        # 创建数据项标签
        item = QLabel(data, self)
        item.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setStyleSheet("background-color: #ff9900; border: 2px solid #cc6600; border-radius: 15px; padding: 5px;")
        item.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        item.resize(40, 40)
        
        # 设置起始位置
        if direction == 'right':
            item.move(10, 15)
            target_x = self.width() - 40
        else:  # 'left'
            item.move(self.width() - 40, 15)
            target_x = 10
            
        # 存储数据项及其属性
        self.flow_items.append({
            'widget': item,
            'direction': direction,
            'target_x': target_x,
            'current_x': item.x(),
            'speed': 3,  # 降低速度使动画更明显
            'completed': False
        })
        
        item.show()
    
    def update_animations(self):
        """更新所有数据项的动画"""
        for item in self.flow_items:
            if not item['completed']:
                if item['direction'] == 'right':
                    item['current_x'] += item['speed']
                    if item['current_x'] >= item['target_x']:
                        item['current_x'] = item['target_x']
                        item['completed'] = True
                else:  # 'left'
                    item['current_x'] -= item['speed']
                    if item['current_x'] <= item['target_x']:
                        item['current_x'] = item['target_x']
                        item['completed'] = True
                
                item['widget'].move(item['current_x'], item['widget'].y())
        
        # 清理已完成的动画
        completed_items = [item for item in self.flow_items if item['completed']]
        for item in completed_items:
            item['widget'].deleteLater()
            self.flow_items.remove(item)
        
        self.update()

class WorkerSignals(QObject):
    """定义信号类，用于线程和主UI通信"""
    buffer_update = pyqtSignal(str, str, str)
    log_message = pyqtSignal(str)
    data_flow = pyqtSignal(str, str, str)  # 新增：数据流动信号 (data, source, target)

class ProducerConsumerUI(QMainWindow):
    """生产者-消费者系统UI定义"""
    def __init__(self):
        super().__init__()
        
        # 设置窗口
        self.setWindowTitle("生产者-消费者系统")
        self.setMinimumSize(800, 600)
        
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
        
        # 缓冲区状态和流动展示
        flow_group = QGroupBox("缓冲区状态与数据流")
        flow_layout = QVBoxLayout()
        
        # 缓冲区和流动管道布局
        buffer_flow_layout = QHBoxLayout()
        
        # 生产者标签
        producer_label = QLabel("生产者")
        producer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        producer_label.setStyleSheet("background-color: #aaffaa; border-radius: 5px; padding: 5px;")
        buffer_flow_layout.addWidget(producer_label)
        
        # 生产者到缓冲区1的管道
        self.producer_to_buffer1 = DataFlowWidget()
        buffer_flow_layout.addWidget(self.producer_to_buffer1)
        
        # 缓冲区1
        self.buffer1_display = QTextEdit()
        self.buffer1_display.setReadOnly(True)
        self.buffer1_display.setMaximumWidth(150)
        buffer_flow_layout.addWidget(self.buffer1_display)
        
        # 缓冲区1到缓冲区2的管道
        self.buffer1_to_buffer2 = DataFlowWidget()
        buffer_flow_layout.addWidget(self.buffer1_to_buffer2)
        
        # 缓冲区2
        self.buffer2_display = QTextEdit()
        self.buffer2_display.setReadOnly(True)
        self.buffer2_display.setMaximumWidth(150)
        buffer_flow_layout.addWidget(self.buffer2_display)
        
        # 缓冲区1到缓冲区3的管道
        self.buffer1_to_buffer3 = DataFlowWidget()
        buffer_flow_layout.addWidget(self.buffer1_to_buffer3)
        
        # 缓冲区3
        self.buffer3_display = QTextEdit()
        self.buffer3_display.setReadOnly(True)
        self.buffer3_display.setMaximumWidth(150)
        buffer_flow_layout.addWidget(self.buffer3_display)
        
        flow_layout.addLayout(buffer_flow_layout)
        flow_group.setLayout(flow_layout)
        main_layout.addWidget(flow_group)
        
        # 日志显示
        log_group = QGroupBox("系统日志")
        log_layout = QVBoxLayout()
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
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
    
    def show_data_flow(self, data, source, target):
        """显示数据流动动画"""
        if source == "producer" and target == "buffer1":
            self.producer_to_buffer1.add_data_item(data, 'right')
        elif source == "buffer1" and target == "buffer2":
            self.buffer1_to_buffer2.add_data_item(data, 'right')
        elif source == "buffer1" and target == "buffer3":
            self.buffer1_to_buffer3.add_data_item(data, 'right')
        elif source == "buffer2" and target == "":  # 消费
            self.buffer2_display.setStyleSheet("background-color: #ff9999; border: 2px solid red;")
            QTimer.singleShot(300, lambda: self.buffer2_display.setStyleSheet(""))
        elif source == "buffer3" and target == "":  # 消费
            self.buffer3_display.setStyleSheet("background-color: #ff9999; border: 2px solid red;")
            QTimer.singleShot(300, lambda: self.buffer3_display.setStyleSheet(""))