import threading
import os
import time
import logging
from buffer import Buffer, Producer, Consumer

# 配置日志记录
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("system.log"),
                        logging.StreamHandler()
                    ])

def producer_thread(buffer1, put_freq):
    """生产者线程函数"""
    thread_id = threading.current_thread().ident
    logging.info(f"生产者线程 {thread_id} 启动")
    producer = Producer(buffer1, put_freq)
    while True:
        producer.put()

def consumer_thread(source_buffer, target_buffer, get_freq, move_freq, consumer_id):
    """消费者线程函数"""
    thread_id = threading.current_thread().ident
    logging.info(f"消费者线程 {consumer_id} {thread_id} 启动")
    
    # 创建一个消费者实例
    consumer = Consumer(source_buffer, get_freq, move_freq)
    
    # 创建两个子线程
    def move_thread():
        sub_thread_id = threading.current_thread().ident
        logging.info(f"消费者 {consumer_id} 的移动线程 {sub_thread_id} 启动")
        while True:
            consumer.move(target_buffer)
    
    def get_thread():
        sub_thread_id = threading.current_thread().ident
        logging.info(f"消费者 {consumer_id} 的获取线程 {sub_thread_id} 启动")
        while True:
            consumer.get()
    
    # 启动子线程
    move_t = threading.Thread(target=move_thread, name=f"MoveThread-C{consumer_id}")
    get_t = threading.Thread(target=get_thread, name=f"GetThread-C{consumer_id}")
    
    move_t.daemon = True
    get_t.daemon = True
    
    move_t.start()
    get_t.start()
    
    # 等待子线程完成（实际上因为是守护线程且有无限循环，这里不会退出）
    move_t.join()
    get_t.join()

def print_buffer_status(buffer1, buffer2, buffer3):
    """打印所有缓冲区状态"""
    # 获取所有锁，确保状态一致性
    logging.info("\n当前缓冲区状态:")
    logging.info(f"缓冲区1: {buffer1}")
    logging.info(f"缓冲区2: {buffer2}")
    logging.info(f"缓冲区3: {buffer3}\n")

def main():
    # 缓冲区大小设置
    size_buffer1 = 8
    size_buffer2 = 1
    size_buffer3 = 4
    
    # 频率设置
    put_freq = 8
    c1_get_freq = 1
    c2_get_freq = 1
    c1_move_freq = 4
    c2_move_freq = 4
    
    # 创建缓冲区
    buffer1 = Buffer(size_buffer1, 1)
    buffer2 = Buffer(size_buffer2, 2)
    buffer3 = Buffer(size_buffer3, 3)
    
    # 创建线程
    p_thread = threading.Thread(target=producer_thread, 
                              args=(buffer1, put_freq), name="ProducerThread")
    
    c1_thread = threading.Thread(target=consumer_thread, 
                               args=(buffer2, buffer1, 
                                     c1_get_freq, c1_move_freq, 1), name="ConsumerThread-1")
    
    c2_thread = threading.Thread(target=consumer_thread, 
                               args=(buffer3, buffer1,
                                     c2_get_freq, c2_move_freq, 2), name="ConsumerThread-2")
    
    # 设置为守护线程，这样主线程退出时这些线程也会退出
    p_thread.daemon = True
    c1_thread.daemon = True
    c2_thread.daemon = True
    
    # 启动线程
    logging.info("系统启动...")
    p_thread.start()
    c1_thread.start()
    c2_thread.start()
    
    try:
        # 主线程保持运行，每秒打印缓冲区状态
        while True:
            time.sleep(3)  # 每3秒打印一次所有缓冲区的状态
            print_buffer_status(buffer1, buffer2, buffer3)
    except KeyboardInterrupt:
        logging.info("\n程序被用户中断")

if __name__ == "__main__":
    main()