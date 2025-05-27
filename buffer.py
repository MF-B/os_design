from queue import Queue
import random
import string
import threading
import time
random.seed(time.time())

class Buffer:
    def __init__(self, size = 0):
        self.data = Queue(maxsize = size)
        self.content = []  # 用于跟踪内容
        self.lock = threading.Lock()

    def put(self, data):
        if type(data) is str and len(data) == 1:
            self.data.put(data)
            self.content.append(data)
        else: print("data must be char")
    
    def get(self):
        temp = self.data.get(timeout=1)
        if self.content:
            self.content.pop(0)
        return temp
    
    def status(self):
        content_str = ''.join(self.content)
        return f"{self.data.qsize()}/{self.data.maxsize} [{content_str}]"
    
    def __str__(self):
        return self.status()

class Producer:
    def __init__(self, buffer, put_freq=2):
        self.buffer = buffer
        self.put_freq = put_freq
        self.lock = threading.Lock()  # 用于保护 put 操作
    def put(self):
        # 生成一个随机字符（从ASCII字母和数字中选择）
        random_char = random.choice(string.ascii_letters + string.digits)
        
        try:
            with self.buffer.lock:
                # 将字符放入buffer
                self.buffer.put(random_char)
                print(f"放入字符 '{random_char}' 到缓冲区 '{self.buffer}'")
                time.sleep(1 / self.put_freq)
                return random_char
        except Exception as e:
            print(f"Producer: 无法放入字符 - {e}")

class Consumer:
    def __init__(self, buffer, get_freq=2, move_freq=2):
        self.buffer = buffer
        self.get_freq = get_freq
        self.move_freq = move_freq
        self.lock = threading.Lock()  # 替换锁为条件变量
    
    def move(self,buffer):
        try:
            with buffer.lock:
                temp = buffer.get()
            with self.buffer.lock:
                self.buffer.put(temp)
                print(f"从缓冲区 '{buffer}' 移动字符 '{temp}' 到缓冲区 '{self.buffer}'")

        except Exception as e:
            print(f"move error: {e}")
        time.sleep(1 / self.move_freq)
    
    def get(self):
        try:
            with self.buffer.lock:
                data = self.buffer.get()
                time.sleep(1 / self.get_freq)
                print(f"从缓冲区 '{self.buffer}' 获取字符 '{data}'")
                return data
        except Exception as e:
            print(f"get error: {e}")