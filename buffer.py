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
    
    def put(self, data):
        if len(self.data) == self.data.maxlen:  # 修正计数方式
            return None
        self.data.append(data)
        return data
    
    def get(self):
        if len(self.data) == 0:  # 修正计数方式
            return None
        data = self.data.popleft()
        return data
    
    def __str__(self):
        return f"Buffer{self.id} {list(self.data)})"

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
            if data:
                print(f"获取字符 '{data}' 从缓冲区 '{before_buf}' ")
                return data

    def move(self, source_buffer):
        time.sleep(1 / self.move_freq)

        with source_buffer.lock, self.buffer.lock:
            source = str(source_buffer)
            data = source_buffer.get()
            if data:
                target = str(self.buffer)
                if self.buffer.put(data):
                    print(f"从缓冲区 '{source}' 移动字符 '{data}' 到缓冲区 '{target}'")
                    return data