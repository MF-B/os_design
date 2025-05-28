from collections import deque
import random
import string
import threading
import time
random.seed(time.time())

class Buffer:
    def __init__(self, size = 10, id = 0):  # 默认值改为10，避免无限缓冲区
        self.id = id
        self.data = deque(maxlen = size)
        self.lock = threading.Condition()

    def can_put(self):
        return len(self.data) < self.data.maxlen
    
    def can_get(self):
        return len(self.data) > 0
    
    def put(self, data):
        with self.lock:
            if not self.can_put():
                self.lock.wait()
            else:
                self.lock.notify_all()
                return self.data.append(data)

    
    def get(self):
        with self.lock:
            if not self.can_get():
                self.lock.wait()
            else:
                data = self.data.popleft()
                self.lock.notify_all()
                return data

    def __str__(self):
        return f"Buffer{self.id} {list(self.data)}"

class Producer:
    def __init__(self, buffer, put_freq=2):
        self.buffer = buffer
        self.put_freq = put_freq
    
    def put(self):
        time.sleep(1 / self.put_freq)
        random_char = random.choice(string.ascii_letters + string.digits)
        if self.buffer.can_put():
            self.buffer.put(random_char)

class Consumer:
    def __init__(self, buffer, get_freq=2, move_freq=2):
        self.buffer = buffer
        self.get_freq = get_freq
        self.move_freq = move_freq
    
    def get(self):
        time.sleep(1 / self.get_freq)
        data = self.buffer.get()
        if data:
            return data
        else:
            return None

    def move(self, source_buffer):
        time.sleep(1 / self.move_freq)
        if source_buffer.can_get() and self.buffer.can_put():
            data = source_buffer.get()
            if data:
                self.buffer.put(data)
            else:
                print("???")