import sys
import logging
from PyQt6.QtWidgets import QApplication
from pc_ui import ProducerConsumerUI
from pc_system import ProducerConsumerSystem

class ProducerConsumerApp:
    """应用程序主类,连接UI与系统逻辑"""
    def __init__(self):
        # 创建UI和系统实例
        self.ui = ProducerConsumerUI()
        self.system = ProducerConsumerSystem()
        
        # 连接信号和槽
        self.setup_connections()
        
    def setup_connections(self):
        """设置UI和系统之间的连接"""
        # 连接系统信号到UI更新
        self.system.signals.buffer_update.connect(self.ui.update_buffer_display)
        self.system.signals.log_message.connect(self.ui.append_log)
        self.system.signals.data_flow.connect(self.ui.animate_data_flow)  # 新增连接
        
        # 连接UI控件到系统功能
        self.ui.start_btn.clicked.connect(self.toggle_system)
        
        # 缓冲区大小调整
        self.ui.buffer1_size.valueChanged.connect(lambda v: self.system.resize_buffer(1, v))
        self.ui.buffer2_size.valueChanged.connect(lambda v: self.system.resize_buffer(2, v))
        self.ui.buffer3_size.valueChanged.connect(lambda v: self.system.resize_buffer(3, v))
        
        # 频率调整
        self.ui.producer_freq.valueChanged.connect(self.system.update_producer_freq)
        self.ui.c1_get_freq.valueChanged.connect(lambda v: self.system.update_consumer_freq(1, 'get', v))
        self.ui.c1_move_freq.valueChanged.connect(lambda v: self.system.update_consumer_freq(1, 'move', v))
        self.ui.c2_get_freq.valueChanged.connect(lambda v: self.system.update_consumer_freq(2, 'get', v))
        self.ui.c2_move_freq.valueChanged.connect(lambda v: self.system.update_consumer_freq(2, 'move', v))
    
    def toggle_system(self):
        """切换系统启动/停止状态"""
        if self.system.running:
            self.system.stop_system()
            self.ui.start_btn.setText("启动系统")
            # 启用参数控制
            self.ui.buffer1_size.setEnabled(True)
            self.ui.buffer2_size.setEnabled(True)
            self.ui.buffer3_size.setEnabled(True)
        else:
            self.system.start_system()
            self.ui.start_btn.setText("停止系统")
            # 禁用某些参数控制
            self.ui.buffer1_size.setEnabled(False)
            self.ui.buffer2_size.setEnabled(False)
            self.ui.buffer3_size.setEnabled(False)
    
    def run(self):
        """运行应用程序"""
        self.ui.show()


if __name__ == "__main__":
    # 配置日志记录
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler("system.log"),
                            logging.StreamHandler()
                        ])

    app = QApplication(sys.argv)
    producer_consumer_app = ProducerConsumerApp()
    producer_consumer_app.run()
    sys.exit(app.exec())