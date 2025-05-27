import sys
import threading
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QSpinBox, 
                            QGroupBox, QTextEdit, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from buffer import Buffer, Producer, Consumer

class WorkerSignals(QObject):
    """定义信号类，用于线程和主UI通信"""
    buffer_update = pyqtSignal(str, str, str)
    log_message = pyqtSignal(str)

class ProducerConsumerSystem:
    """系统逻辑类，管理缓冲区和线程"""
    def __init__(self):
        # 创建信号对象
        self.signals = WorkerSignals()
        
        # 创建缓冲区
        self.buffer1 = Buffer(8, 1)
        self.buffer2 = Buffer(4, 2)
        self.buffer3 = Buffer(4, 3)
        
        # 设置默认频率
        self.put_freq = 2
        self.c1_get_freq = 1
        self.c2_get_freq = 1
        self.c1_move_freq = 2
        self.c2_move_freq = 2
        
        # 控制线程的标志
        self.running = False
        self.threads = []
    
    def start_system(self):
        """启动系统"""
        if self.running:
            return
        
        self.running = True
        
        # 创建线程
        p_thread = threading.Thread(target=self.producer_thread)
        c1_thread = threading.Thread(target=self.consumer_thread, 
                                   args=(self.buffer2, self.buffer1, 
                                         self.c1_get_freq, self.c1_move_freq, 1))
        c2_thread = threading.Thread(target=self.consumer_thread, 
                                   args=(self.buffer3, self.buffer1,
                                         self.c2_get_freq, self.c2_move_freq, 2))
        
        # 设置为守护线程
        p_thread.daemon = True
        c1_thread.daemon = True
        c2_thread.daemon = True
        
        # 记录线程
        self.threads = [p_thread, c1_thread, c2_thread]
        
        # 启动线程
        p_thread.start()
        c1_thread.start()
        c2_thread.start()
        
        # 启动状态更新线程
        status_thread = threading.Thread(target=self.update_status)
        status_thread.daemon = True
        status_thread.start()
        self.threads.append(status_thread)
        
        self.signals.log_message.emit("系统已启动")
    
    def stop_system(self):
        """停止系统"""
        if not self.running:
            return
        
        self.running = False
        # 线程是守护线程，主线程结束后会自动结束
        # 这里只需要更新系统状态
        self.signals.log_message.emit("系统已停止")
    
    def producer_thread(self):
        """生产者线程函数"""
        thread_id = threading.current_thread().ident
        self.signals.log_message.emit(f"生产者线程 {thread_id} 启动")
        producer = Producer(self.buffer1, self.put_freq)
        
        while self.running:
            result = producer.put()
            if result:
                self.signals.log_message.emit(f"放入字符 '{result}' 到缓冲区 '{self.buffer1}'")
    
    def consumer_thread(self, source_buffer, target_buffer, get_freq, move_freq, consumer_id):
        """消费者线程函数"""
        thread_id = threading.current_thread().ident
        self.signals.log_message.emit(f"消费者线程 {consumer_id} {thread_id} 启动")
        
        # 创建一个消费者实例
        consumer = Consumer(source_buffer, get_freq, move_freq)
        
        # 创建两个子线程
        def move_thread():
            sub_thread_id = threading.current_thread().ident
            self.signals.log_message.emit(f"消费者 {consumer_id} 的移动线程 {sub_thread_id} 启动")
            while self.running:
                consumer.move(target_buffer)
        
        def get_thread():
            sub_thread_id = threading.current_thread().ident
            self.signals.log_message.emit(f"消费者 {consumer_id} 的获取线程 {sub_thread_id} 启动")
            while self.running:
                consumer.get()
        
        # 启动子线程
        move_t = threading.Thread(target=move_thread)
        get_t = threading.Thread(target=get_thread)
        
        move_t.daemon = True
        get_t.daemon = True
        
        move_t.start()
        get_t.start()
        
        # 将子线程添加到线程列表以便跟踪
        self.threads.extend([move_t, get_t])
        
        # 等待子线程完成
        while self.running:
            time.sleep(0.1)
    
    def update_status(self):
        """更新状态线程"""
        while self.running:
            time.sleep(1)  # 每秒更新一次
            # 获取所有锁，确保状态一致性
            with self.buffer1.lock, self.buffer2.lock, self.buffer3.lock:
                buffer1_str = str(self.buffer1)
                buffer2_str = str(self.buffer2)
                buffer3_str = str(self.buffer3)
                
            # 发送信号更新UI
            self.signals.buffer_update.emit(buffer1_str, buffer2_str, buffer3_str)
    
    def update_producer_freq(self, value):
        """更新生产者频率"""
        self.put_freq = value
        self.signals.log_message.emit(f"生产者频率更新为: {value}")
    
    def update_consumer_freq(self, consumer_id, freq_type, value):
        """更新消费者频率
        consumer_id: 1 或 2
        freq_type: 'get' 或 'move'
        value: 新的频率值
        """
        if consumer_id == 1:
            if freq_type == 'get':
                self.c1_get_freq = value
            else:
                self.c1_move_freq = value
        else:
            if freq_type == 'get':
                self.c2_get_freq = value
            else:
                self.c2_move_freq = value
                
        self.signals.log_message.emit(f"消费者 {consumer_id} {freq_type}频率更新为: {value}")
    
    def resize_buffer(self, buffer_id, size):
        """调整缓冲区大小"""
        if buffer_id == 1:
            new_buffer = Buffer(size, 1)
            with self.buffer1.lock:
                # 复制旧缓冲区中的数据
                for item in list(self.buffer1.data):
                    if new_buffer.can_put():
                        new_buffer.put(item)
                self.buffer1 = new_buffer
        elif buffer_id == 2:
            new_buffer = Buffer(size, 2)
            with self.buffer2.lock:
                for item in list(self.buffer2.data):
                    if new_buffer.can_put():
                        new_buffer.put(item)
                self.buffer2 = new_buffer
        else:
            new_buffer = Buffer(size, 3)
            with self.buffer3.lock:
                for item in list(self.buffer3.data):
                    if new_buffer.can_put():
                        new_buffer.put(item)
                self.buffer3 = new_buffer
                
        self.signals.log_message.emit(f"缓冲区 {buffer_id} 大小调整为: {size}")


class MainWindow(QMainWindow):
    """主窗口类"""
    def __init__(self):
        super().__init__()
        
        # 创建系统实例
        self.system = ProducerConsumerSystem()
        
        # 连接信号
        self.system.signals.buffer_update.connect(self.update_buffer_display)
        self.system.signals.log_message.connect(self.append_log)
        
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
        self.start_btn.clicked.connect(self.toggle_system)
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
        self.buffer1_size.valueChanged.connect(lambda v: self.system.resize_buffer(1, v))
        params_layout.addWidget(self.buffer1_size, 0, 1)
        
        params_layout.addWidget(QLabel("缓冲区2大小:"), 0, 2)
        self.buffer2_size = QSpinBox()
        self.buffer2_size.setRange(1, 20)
        self.buffer2_size.setValue(4)
        self.buffer2_size.valueChanged.connect(lambda v: self.system.resize_buffer(2, v))
        params_layout.addWidget(self.buffer2_size, 0, 3)
        
        params_layout.addWidget(QLabel("缓冲区3大小:"), 0, 4)
        self.buffer3_size = QSpinBox()
        self.buffer3_size.setRange(1, 20)
        self.buffer3_size.setValue(4)
        self.buffer3_size.valueChanged.connect(lambda v: self.system.resize_buffer(3, v))
        params_layout.addWidget(self.buffer3_size, 0, 5)
        
        # 频率设置
        params_layout.addWidget(QLabel("生产者频率:"), 1, 0)
        self.producer_freq = QSpinBox()
        self.producer_freq.setRange(1, 10)
        self.producer_freq.setValue(2)
        self.producer_freq.valueChanged.connect(self.system.update_producer_freq)
        params_layout.addWidget(self.producer_freq, 1, 1)
        
        # 消费者1频率
        params_layout.addWidget(QLabel("消费者1获取频率:"), 1, 2)
        self.c1_get_freq = QSpinBox()
        self.c1_get_freq.setRange(1, 10)
        self.c1_get_freq.setValue(1)
        self.c1_get_freq.valueChanged.connect(lambda v: self.system.update_consumer_freq(1, 'get', v))
        params_layout.addWidget(self.c1_get_freq, 1, 3)
        
        params_layout.addWidget(QLabel("消费者1移动频率:"), 1, 4)
        self.c1_move_freq = QSpinBox()
        self.c1_move_freq.setRange(1, 10)
        self.c1_move_freq.setValue(2)
        self.c1_move_freq.valueChanged.connect(lambda v: self.system.update_consumer_freq(1, 'move', v))
        params_layout.addWidget(self.c1_move_freq, 1, 5)
        
        # 消费者2频率
        params_layout.addWidget(QLabel("消费者2获取频率:"), 2, 2)
        self.c2_get_freq = QSpinBox()
        self.c2_get_freq.setRange(1, 10)
        self.c2_get_freq.setValue(1)
        self.c2_get_freq.valueChanged.connect(lambda v: self.system.update_consumer_freq(2, 'get', v))
        params_layout.addWidget(self.c2_get_freq, 2, 3)
        
        params_layout.addWidget(QLabel("消费者2移动频率:"), 2, 4)
        self.c2_move_freq = QSpinBox()
        self.c2_move_freq.setRange(1, 10)
        self.c2_move_freq.setValue(2)
        self.c2_move_freq.valueChanged.connect(lambda v: self.system.update_consumer_freq(2, 'move', v))
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
    
    def toggle_system(self):
        """切换系统启动/停止状态"""
        if self.system.running:
            self.system.stop_system()
            self.start_btn.setText("启动系统")
            # 启用参数控制
            self.buffer1_size.setEnabled(True)
            self.buffer2_size.setEnabled(True)
            self.buffer3_size.setEnabled(True)
        else:
            self.system.start_system()
            self.start_btn.setText("停止系统")
            # 禁用某些参数控制
            self.buffer1_size.setEnabled(False)
            self.buffer2_size.setEnabled(False)
            self.buffer3_size.setEnabled(False)
    
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
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.system.stop_system()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())