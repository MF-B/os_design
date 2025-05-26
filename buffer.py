import queue
from queue import Queue
import random
import string
import time
random.seed(time.time())

class Buffer:
    def __init__(self, size = 0):
        self.data = Queue(maxsize = size)
    def put(self, data):
        if type(data) is str and len(data) == 1:
            self.data.put(data)
        else: print("data must be char")
    def move(self,buffer):
        temp = buffer.data.get()
        self.data.put(temp)
        return temp
    def get(self):
        return self.data.get()

class Producer:
    def __init__(self, buffer, put_freq=2):
        self.buffer = buffer
        self.put_freq = put_freq
    def put(self):
        # 生成一个随机字符（从ASCII字母和数字中选择）
        random_char = random.choice(string.ascii_letters + string.digits)
        
        try:
            # 将字符放入buffer
            self.buffer.put(random_char)
        except Exception as e:
            print(f"Producer: 无法放入字符 - {e}")
        # 按照频率添加延迟
        # 频率为put_freq Hz，意味着每1/put_freq秒执行一次
        time.sleep(1 / self.put_freq)

class Consumer:
    def __init__(self, buffer, get_freq=2, move_freq=2):
        self.buffer = buffer
        self.get_freq = get_freq
        self.move_freq = move_freq
    def move(self,buffer):
        try:
            data = self.buffer.move(buffer)
        except Exception as e:
            print(f"move error: {e}")
        time.sleep(1 / self.move_freq)
    def get(self):
        try:
            data = self.buffer.get()
        except Exception as e:
            print(f"get error: {e}")
        time.sleep(1 / self.get_freq)
        return data