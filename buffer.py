from queue import Queue


class Buffer:
    def __init__(self, size = 0):
        self.data = Queue(maxsize = size)
    def put(self, data):
        if type(data) is str and len(data) == 1:
            self.data.put(data)
        else: raise TypeError('data must be char')
    def get(self):
        if not self.data.empty():
            return self.data.get()
        return None