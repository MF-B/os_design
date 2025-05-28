from collections import deque
import random
import string
import threading
import time
import logging
random.seed(time.time())

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
            while len(self.data) == self.data.maxlen:
                logger.debug(f"Buffer {self.id} is full, producer waiting.")
                self.condition.wait()
                
            self.data.append(data)
            logger.debug(f"Buffer {self.id} put data: {data}, current size: {len(self.data)}")
            self.condition.notify_all()
            return data
    
    def get(self):
        with self.condition:
            while len(self.data) == 0:
                logger.debug(f"Buffer {self.id} is empty, consumer waiting.")
                self.condition.wait()
                
            data = self.data.popleft()
            logger.debug(f"Buffer {self.id} get data: {data}, current size: {len(self.data)}")
            self.condition.notify_all()
            return data
        
    def resize(self, new_size):
        """
        调整缓冲区的大小。
        如果新大小小于当前元素数量，则保留最早的元素。
        """
        with self.condition:
            if not isinstance(new_size, int) or new_size <= 0:
                logger.warning(f"Buffer {self.id} resize: 无效的大小 {new_size}。必须是正整数。")
                return False # 表示操作失败

            current_items = list(self.data)
            
            # 如果缩小缓冲区，保留最左边（最早）的元素
            if new_size < len(current_items):
                items_to_keep = current_items[:new_size]
            else:
                items_to_keep = current_items # 如果扩大或大小不变，保留所有元素
            
            self.data = deque(items_to_keep, maxlen=new_size)
            
            logger.info(f"Buffer {self.id} 已调整大小为 {new_size}。当前元素: {len(self.data)}/{self.data.maxlen}.")
            # 通知所有等待的线程，因为缓冲区的容量和/或内容可能已更改
            self.condition.notify_all()
            return True
    
    def __str__(self):
        return f"Buffer{self.id} {list(self.data)}"

class Producer:
    def __init__(self, buffer, put_freq=2):
        self.buffer = buffer
        self.put_freq = max(put_freq, 0.1)
        logger.info(f"Producer initialized for Buffer {self.buffer.id} with put_freq {self.put_freq}")

    def set_put_freq(self, freq):
        """设置生产者放入数据的频率"""
        if freq <= 0:
            logger.warning("生产者频率必须大于0，已设置为默认值2。")
            self.put_freq = 2
        else:
            self.put_freq = freq
        logger.info(f"Producer put frequency set to {self.put_freq}")
    
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
        self.buffer = buffer
        self.get_freq = max(get_freq, 0.1)
        self.move_freq = max(move_freq, 0.1)
        logger.info(f"Consumer initialized for Buffer {self.buffer.id} with get_freq {self.get_freq}, move_freq {self.move_freq}")

    def set_get_freq(self, freq):
        """设置消费者获取数据的频率"""
        if freq <= 0:
            logger.warning("消费者获取频率必须大于0，已设置为默认值2。")
            self.get_freq = 2
        else:
            self.get_freq = freq
        logger.info(f"Consumer get frequency set to {self.get_freq}")

    def set_move_freq(self, freq):
        """设置消费者移动数据的频率"""
        if freq <= 0:
            logger.warning("消费者移动频率必须大于0，已设置为默认值2。")
            self.move_freq = 2
        else:
            self.move_freq = freq
        logger.info(f"Consumer move frequency set to {self.move_freq}")
    
    def get(self):
        time.sleep(1 / self.get_freq)
        try:
            data = self.buffer.get()
            logger.info(f"Consumer got '{data}' from Buffer {self.buffer.id}")
            return data
        except Exception as e:
            logger.error(f"消费者获取数据失败: {e}", exc_info=True)
            raise

    def move(self, source_buffer):
        time.sleep(1 / self.move_freq)
        try:
            data = source_buffer.get()
            self.buffer.put(data)
            logger.info(f"Consumer moved '{data}' from Buffer {source_buffer.id} to Buffer {self.buffer.id}")
            return data
        except Exception as e:
            logger.error(f"移动操作失败: {e}", exc_info=True)
            raise
