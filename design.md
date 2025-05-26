# 数据结构
## Buffer
### 定义
```python
class Buffer:
    def __init__(self, size = 0):
        self.data = Queue(maxsize = size)
    def put(self, data)
    def get(self)
```
## 生产者(Producer)
```python
class Producer:
    def __init__(
        self,
        buffer,
        put_freq=2, # put的速度是1秒2次,即2HZ
    ):
    
```
## 消费者(Consumer)
```python
class Consumer:
    def __init__(
        self, 
        buffer, 
        get_freq=2, 
        move_freq=2,
    ):
```