import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QSpinBox, 
                            QGroupBox, QTextEdit, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject

class WorkerSignals(QObject):
    """定义信号类，用于线程和主UI通信"""
    buffer_update = pyqtSignal(str, str, str)
    log_message = pyqtSignal(str)

class freq_updata(QObject):
    put_freq_update = pyqtSignal()
    move_freq_update = pyqtSignal()
    get_freq_update = pyqtSignal()

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
        
        # 缓冲区状态显示
        buffer_group = QGroupBox("缓冲区状态")
        buffer_layout = QHBoxLayout()
        
        self.buffer1_display = QTextEdit()
        self.buffer1_display.setReadOnly(True)
        buffer_layout.addWidget(self.buffer1_display)
        
        self.buffer2_display = QTextEdit()
        self.buffer2_display.setReadOnly(True)
        buffer_layout.addWidget(self.buffer2_display)
        
        self.buffer3_display = QTextEdit()
        self.buffer3_display.setReadOnly(True)
        buffer_layout.addWidget(self.buffer3_display)
        
        buffer_group.setLayout(buffer_layout)
        main_layout.addWidget(buffer_group)
        
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