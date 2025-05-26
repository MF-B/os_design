from queue import Queue


class Buffer:
    def __init__(self, size = 0):
        self.data = Queue(maxsize = size)
    def put(self, data):
        if type(data) is str and len(data) == 1:
            self.data.put(data)
        else: raise TypeError('data must be char')
    def move(self,buffer):
        temp = buffer.data.put()
        self.data.get(temp)
    def get(self):
        if not self.data.empty():
            return self.data.get()
        return None

class Producer:
    def __init__(self, buffer, put_freq=2):
        self.buffer = buffer
        self.put_freq = put_freq

class Consumer:
    def __init__(self, buffer, get_freq=2, move_freq=2):
        self.buffer = buffer
        self.get_freq = get_freq
        self.move_freq = move_freq
    def move(self,buffer):
        self.buffer.move(buffer)
    def get(self):
        self.buffer.get()