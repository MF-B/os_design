from collections import deque
import random
import string
import threading
import time
import logging # 导入 logging 模块
random.seed(time.time())

# 获取一个 logger 实例
logger = logging.getLogger(__name__)

class Buffer:
    def __init__(self, size = 10, id=0):
        self.id = id
        self.data = deque(maxlen = size)
        self.condition = threading.Condition()
        logger.info(f"Buffer {self.id} initialized with size {size}")
    
    def can_put(self):
        return len(self.data) < self.data.maxlen
    
    def can_get(self):
        return len(self.data) > 0
    
    def put(self, data):
        with self.condition:
            # 当缓冲区满时等待
            while len(self.data) == self.data.maxlen:
                logger.debug(f"Buffer {self.id} is full, producer waiting.")
                self.condition.wait()
                
            self.data.append(data)
            logger.debug(f"Buffer {self.id} put data: {data}, current size: {len(self.data)}")
            # 通知可能在等待获取数据的消费者
            self.condition.notify_all()
            return data
    
    def get(self):
        with self.condition:
            # 当缓冲区空时等待
            while len(self.data) == 0:
                logger.debug(f"Buffer {self.id} is empty, consumer waiting.")
                self.condition.wait()
                
            data = self.data.popleft()
            logger.debug(f"Buffer {self.id} get data: {data}, current size: {len(self.data)}")
            # 通知可能在等待放入数据的生产者
            self.condition.notify_all()
            return data
    
    def __str__(self):
        return f"Buffer{self.id} {list(self.data)}"

class Producer:
    def __init__(self, buffer, put_freq=2):
        self.buffer = buffer
        self.put_freq = max(put_freq, 0.1)
        logger.info(f"Producer initialized for Buffer {self.buffer.id} with put_freq {self.put_freq}")
    
    def put(self):
        time.sleep(1 / self.put_freq)
        random_char = random.choice(string.ascii_letters + string.digits)
        try:
            data = self.buffer.put(random_char)
            logger.info(f"Producer put '{data}' into Buffer {self.buffer.id}")
            return data
        except Exception as e:
            logger.error(f"生产者放入数据失败: {e}", exc_info=True)
            raise

class Consumer:
    def __init__(self, buffer, get_freq=2, move_freq=2):
        self.buffer = buffer # 这个 buffer 是消费者自身要操作的 buffer (即 source_buffer)
        self.get_freq = max(get_freq, 0.1)
        self.move_freq = max(move_freq, 0.1)
        logger.info(f"Consumer initialized for Buffer {self.buffer.id} with get_freq {self.get_freq}, move_freq {self.move_freq}")
    
    def get(self):
        time.sleep(1 / self.get_freq)
        try:
            data = self.buffer.get() # 从自身的 buffer (source_buffer) 获取数据
            logger.info(f"Consumer got '{data}' from Buffer {self.buffer.id}")
            return data
        except Exception as e:
            logger.error(f"消费者获取数据失败: {e}", exc_info=True)
            raise

    def move(self, target_buffer): # target_buffer 是要移动到的目标缓冲区
        time.sleep(1 / self.move_freq)
        
        try:
            # 注意：这里的逻辑是 Consumer 从 target_buffer 获取数据，然后放入自己的 buffer
            # 这可能与通常的 "从 source_buffer 移动到 target_buffer" 的理解相反
            # 如果意图是从 Consumer 自己的 buffer (self.buffer) 移动到 target_buffer，则需要调整
            data = target_buffer.get() # 从 target_buffer 获取
            self.buffer.put(data)      # 放入 self.buffer (即 Consumer 初始化的 buffer)
            logger.info(f"Consumer moved '{data}' from Buffer {target_buffer.id} to Buffer {self.buffer.id}")
            return data
        except Exception as e:
            logger.error(f"移动操作失败: {e}", exc_info=True)
            raise