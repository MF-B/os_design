from collections import deque
import random
import string
import threading
import time
random.seed(time.time())

class Buffer:
    def __init__(self, size = 10, id=0):  # 默认值改为10，避免无限缓冲区
        self.id = id
        self.data = deque(maxlen = size)
        self.lock = threading.Lock()

    def can_put(self):
        return len(self.data) < self.data.maxlen
    
    def can_get(self):
        return len(self.data) > 0
    
    def put(self, data):
        if len(self.data) == self.data.maxlen:  # 修正计数方式
            return None
        else: 
            self.data.append(data)
            return data
    
    def get(self):
        if len(self.data) == 0:  # 修正计数方式
            return None
        data = self.data.popleft()
        return data
    
    def __str__(self):
        return f"Buffer{self.id} {list(self.data)}"

# Producer和Consumer类保持不变
class Producer:
    def __init__(self, buffer, put_freq=2):
        self.buffer = buffer
        self.put_freq = put_freq
    
    def put(self):
        time.sleep(1 / self.put_freq)
        random_char = random.choice(string.ascii_letters + string.digits)
        with self.buffer.lock:
            if self.buffer.put(random_char):
                print(f"放入字符 '{random_char}' 到缓冲区 '{self.buffer}'")
                return random_char
            else:
                print(f"缓冲区 '{self.buffer}' 已满，无法放入字符 '{random_char}'")
                return None

class Consumer:
    def __init__(self, buffer, get_freq=2, move_freq=2):
        self.buffer = buffer
        self.get_freq = get_freq
        self.move_freq = move_freq
    
    def get(self):
        time.sleep(1 / self.get_freq)
        with self.buffer.lock:
            before_buf = str(self.buffer)
            data = self.buffer.get()
            after_buf = str(self.buffer)  # 添加这行
            if data:
                print(f"获取字符 '{data}' 从缓冲区 '{before_buf}' -> 现在为 '{after_buf}'")
                return data
            else:
                print(f"缓冲区 '{self.buffer}' 为空，无法获取数据")
                return None

    def move(self, source_buffer):
        time.sleep(1 / self.move_freq)

        # 确保两个锁都被获取，防止死锁，始终按相同顺序获取锁
        with source_buffer.lock:
            with self.buffer.lock:
                # 先获取操作前的状态
                source_before = str(source_buffer)
                target_before = str(self.buffer)
                
                # 执行操作
                if source_buffer.can_get() and self.buffer.can_put():
                    data = source_buffer.get()
                    if data:
                        self.buffer.put(data)
                        # 获取操作后的状态
                        print(f"移动字符 '{data}' 从缓冲区 '{source_before}' 到缓冲区 '{target_before}'")
                    else:
                        print(f"源缓冲区 '{source_buffer}' 为空，无法移动数据")