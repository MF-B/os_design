import threading
import os
import time
from buffer import Buffer, Producer, Consumer

buffer1_lock = threading.Lock()
buffer2_lock = threading.Lock()
buffer3_lock = threading.Lock()

def producer_thread(buffer1, put_freq):
    """生产者线程函数"""
    thread_id = threading.current_thread().ident
    print(f"生产者线程 {thread_id} 启动")
    producer = Producer(buffer1, put_freq)
    while True:
        producer.put()
        time.sleep(1/put_freq)

def consumer_thread(source_buffer, target_buffer, get_freq, move_freq, consumer_id):
    """消费者线程函数"""
    thread_id = threading.current_thread().ident
    print(f"消费者线程 {consumer_id} {thread_id} 启动")
    
    # 创建一个消费者实例
    consumer = Consumer(source_buffer, get_freq, move_freq)
    
    # 创建两个子线程
    def move_thread():
        sub_thread_id = threading.current_thread().ident
        print(f"消费者 {consumer_id} 的移动线程 {sub_thread_id} 启动")
        while True:
            consumer.move(target_buffer)
            time.sleep(1/move_freq)
    
    def get_thread():
        sub_thread_id = threading.current_thread().ident
        print(f"消费者 {consumer_id} 的获取线程 {sub_thread_id} 启动")
        while True:
            consumer.get()
            time.sleep(1/get_freq)
    
    # 启动子线程
    move_t = threading.Thread(target=move_thread)
    get_t = threading.Thread(target=get_thread)
    
    move_t.daemon = True
    get_t.daemon = True
    
    move_t.start()
    get_t.start()
    
    # 等待子线程完成（实际上因为是守护线程且有无限循环，这里不会退出）
    move_t.join()
    get_t.join()

def print_buffer_status(buffer1, buffer2, buffer3):
    """打印所有缓冲区状态"""
    print("\n当前缓冲区状态:")
    print(f"缓冲区1: {buffer1}")
    print(f"缓冲区2: {buffer2}")
    print(f"缓冲区3: {buffer3}\n")

def main():
    # 缓冲区大小设置
    size_buffer1 = 4
    size_buffer2 = 8
    size_buffer3 = 8
    
    # 频率设置
    put_freq = 4
    c1_get_freq = 1
    c2_get_freq = 1
    c1_move_freq = 1
    c2_move_freq = 1
    
    # 创建缓冲区
    buffer1 = Buffer(size_buffer1)
    buffer2 = Buffer(size_buffer2)
    buffer3 = Buffer(size_buffer3)
    
    # 创建线程
    p_thread = threading.Thread(target=producer_thread, 
                              args=(buffer1, put_freq))
    
    c1_thread = threading.Thread(target=consumer_thread, 
                               args=(buffer1, buffer2, 
                                     c1_get_freq, c1_move_freq, 1))
    
    c2_thread = threading.Thread(target=consumer_thread, 
                               args=(buffer1, buffer3,
                                     c2_get_freq, c2_move_freq, 2))
    
    # 设置为守护线程，这样主线程退出时这些线程也会退出
    p_thread.daemon = True
    c1_thread.daemon = True
    c2_thread.daemon = True
    
    # 启动线程
    print("系统启动...")
    p_thread.start()
    c1_thread.start()
    c2_thread.start()
    
    try:
        # 主线程保持运行，每秒打印缓冲区状态
        while True:
            time.sleep(3)  # 每3秒打印一次所有缓冲区的状态
            print_buffer_status(buffer1, buffer2, buffer3)
    except KeyboardInterrupt:
        print("\n程序被用户中断")

if __name__ == "__main__":
    main()