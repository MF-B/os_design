from queue import Queue


class Buffer:
    def __init__(self, size = 0):
        self.data = Queue(maxsize = size)
    def put(self, data):
        self.data.put(data)
    def get(self):
        if not self.data.empty():
            return self.data.get()
        return None

