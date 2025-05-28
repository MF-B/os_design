import threading
import time
import logging
from PyQt6.QtCore import QObject, pyqtSignal
from buffer import Buffer, Producer, Consumer

# 获取一个 logger 实例
logger = logging.getLogger(__name__)

class QtLogHandler(logging.Handler):
    def __init__(self, log_signal_emitter):
        super().__init__()
        self.log_signal_emitter = log_signal_emitter
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_signal_emitter.emit(msg)
        except Exception:
            self.handleError(record)

class WorkerSignals(QObject):
    """定义信号类，用于线程和主UI通信"""
    buffer_update = pyqtSignal(str, str, str)
    log_message = pyqtSignal(str)


class ProducerConsumerSystem:
    """系统逻辑类，管理缓冲区和线程"""
    def __init__(self):
        # 创建信号对象
        self.signals = WorkerSignals()

        # logging模块的日志路由到UI
        self._setup_ui_logging()
        
        # 创建缓冲区
        self.buffer1 = Buffer(8, 1)
        self.buffer2 = Buffer(4, 2)
        self.buffer3 = Buffer(4, 3)
        
        # 设置默认频率
        self.put_freq = 4
        self.c1_get_freq = 1
        self.c2_get_freq = 1
        self.c1_move_freq = 2
        self.c2_move_freq = 2
        
        # 控制线程的标志
        self.running = False
        self.threads = []

    def _setup_ui_logging(self):
        """配置logging模块,使其日志消息通过信号发送到UI"""
        qt_handler = QtLogHandler(self.signals.log_message)
        qt_handler.setLevel(logging.INFO)  # 你可以根据需要设置不同的日志级别

        """
        将处理器添加到根logger,以捕获所有模块的日志
        或者你可以选择性地添加到特定的logger,例如:
        logging.getLogger('buffer').addHandler(qt_handler)
        logging.getLogger(__name__).addHandler(qt_handler) # __name__ 在这里是 'pc_system'
        logging.getLogger().addHandler(qt_handler)
        """
        logging.getLogger().addHandler(qt_handler)
    
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

        log_msg = "系统已启动"
        self.signals.log_message.emit(log_msg)
        logger.info(log_msg)
    
    def stop_system(self):
        """停止系统"""
        if not self.running:
            return
        
        self.running = False
        log_msg = "系统已停止"
        self.signals.log_message.emit(log_msg)
        logger.info(log_msg)
    
    def producer_thread(self):
        """生产者线程函数"""
        thread_id = threading.current_thread().ident
        log_msg = f"生产者线程 {thread_id} 启动"
        self.signals.log_message.emit(log_msg)
        logger.info(log_msg)
        producer = Producer(self.buffer1, self.put_freq)
        while self.running:
            producer.set_put_freq(self.put_freq)
            producer.put()
    
    def consumer_thread(self, source_buffer, target_buffer, get_freq, move_freq, consumer_id):
        """消费者线程函数"""
        thread_id = threading.current_thread().ident
        log_msg = f"消费者线程 {consumer_id} {thread_id} 启动"
        self.signals.log_message.emit(log_msg)
        logger.info(log_msg)
        
        # 创建一个消费者实例
        consumer = Consumer(source_buffer, get_freq, move_freq)
        
        # 创建两个子线程
        def move_thread():
            sub_thread_id = threading.current_thread().ident
            move_log_msg = f"消费者 {consumer_id} 的MOVE线程 {sub_thread_id} 启动"
            self.signals.log_message.emit(move_log_msg)
            logger.info(move_log_msg)
            while self.running:
                consumer.set_move_freq(move_freq)
                consumer.move(target_buffer)
        
        def get_thread():
            sub_thread_id = threading.current_thread().ident
            get_log_msg = f"消费者 {consumer_id} 的GET线程 {sub_thread_id} 启动"
            self.signals.log_message.emit(get_log_msg)
            logger.info(get_log_msg)
            while self.running:
                consumer.set_get_freq(get_freq)
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
            time.sleep(0.1)  # 每100ms秒更新一次
            buffer1_str = str(self.buffer1)
            buffer2_str = str(self.buffer2)
            buffer3_str = str(self.buffer3)
                
            # 发送信号更新UI
            self.signals.buffer_update.emit(buffer1_str, buffer2_str, buffer3_str)
    
    def update_producer_freq(self, value):
        """更新生产者频率"""
        self.put_freq = value
        log_msg = f"生产者频率更新为: {value}"
        self.signals.log_message.emit(log_msg)
        logger.info(log_msg)
    
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
                
        log_msg = f"消费者 {consumer_id} {freq_type}频率更新为: {value}"
        self.signals.log_message.emit(log_msg)
        logger.info(log_msg)
    
    def resize_buffer(self, buffer_id, size):
        """调整缓冲区大小"""
        
        target_buffer = None
        if buffer_id == 1:
            target_buffer = self.buffer1
        elif buffer_id == 2:
            target_buffer = self.buffer2
        elif buffer_id == 3:
            target_buffer = self.buffer3
        
        if not target_buffer:
            log_msg = f"调整缓冲区大小失败：无效的缓冲区ID {buffer_id}。"
            self.signals.log_message.emit(log_msg)
            logger.warning(log_msg)
            return

        if not isinstance(size, int) or size <= 0:
            log_msg = f"调整缓冲区 {buffer_id} 大小失败：大小 '{size}' 必须是一个正整数。"
            self.signals.log_message.emit(log_msg)
            logger.warning(log_msg)
            return

        # 调用 Buffer 实例的 resize 方法
        success = target_buffer.resize(size)
        
        if success:
            log_msg = f"缓冲区 {buffer_id} 大小已成功调整为: {size}。"
            self.signals.log_message.emit(log_msg)
            logger.info(log_msg)
        else:
            # 此情况主要用于 Buffer.resize 内部发现问题 (例如，无效大小),
            # 尽管 pc_system 也已检查。
            # Buffer.resize 方法本身会记录其警告。
            log_msg = f"尝试调整缓冲区 {buffer_id} 大小为 {size}，但操作未完成 (详见缓冲区日志)。"
            self.signals.log_message.emit(log_msg)
            logger.warning(log_msg)