import unittest
from buffer import Buffer, Producer, Consumer
import time
import random
import string

class TestProducer(unittest.TestCase):
    def test_producer_put(self):
        """测试Producer的put方法是否能正常向Buffer中放入字符"""
        print("\n===== 测试Producer的put方法 =====")
        # 创建一个大小为5的Buffer
        test_buffer = Buffer(size=5)
        
        # 创建一个Producer，设置较高的频率以便快速测试
        producer = Producer(test_buffer, put_freq=1)
        
        # 初始时Buffer应该为空
        self.assertTrue(test_buffer.data.empty())
        print("初始状态: Buffer为空")
        
        # 调用put方法3次
        for i in range(3):
            char = producer.put()
            print(f"第{i+1}次put: 放入字符 '{char}', Buffer大小: {test_buffer.data.qsize()}")
        
        # 验证Buffer中现在应该有3个元素
        self.assertEqual(test_buffer.data.qsize(), 3)
        print(f"验证完成: Buffer中有 {test_buffer.data.qsize()} 个元素")
        
        # 从Buffer中获取这些元素，确保它们都是单个字符
        for i in range(3):
            char = test_buffer.get()
            print(f"获取第{i+1}个元素: '{char}'")
            self.assertIsInstance(char, str)
            self.assertEqual(len(char), 1)
    
    def test_producer_frequency(self):
        """测试Producer的put频率是否正确"""
        print("\n===== 测试Producer的put频率 =====")
        test_buffer = Buffer(size=10)
        
        # 创建一个频率为5Hz的Producer（每0.5秒执行一次）
        producer = Producer(test_buffer, put_freq=2)
        print(f"创建Producer，put频率: 2Hz (每0.5秒一次)")
        
        # 记录开始时间
        start_time = time.time()
        print(f"开始时间: {start_time:.3f}")
        
        # 执行2次put操作
        char1 = producer.put()
        print(f"第1次put: 放入字符 '{char1}', 时间: {time.time():.3f}")
        char2 = producer.put()
        print(f"第2次put: 放入字符 '{char2}', 时间: {time.time():.3f}")
        
        # 计算经过的时间
        elapsed_time = time.time() - start_time
        print(f"总耗时: {elapsed_time:.3f}秒")
        
        # 验证经过的时间约为0.4秒（允许有小误差）
        self.assertAlmostEqual(elapsed_time, 1, delta=0.1)
        print(f"验证完成: 耗时接近1秒，实际为{elapsed_time:.3f}秒")

class TestConsumer(unittest.TestCase):
    def test_consumer_get(self):
        """测试Consumer的get方法是否能正常从Buffer中获取字符"""
        print("\n===== 测试Consumer的get方法 =====")
        # 创建一个大小为5的Buffer
        test_buffer = Buffer(size=5)
        
        # 先向buffer中放入3个元素
        test_chars = []
        for i in range(3):
            char = random.choice(string.ascii_letters + string.digits)
            test_chars.append(char)
            test_buffer.put(char)
            print(f"向Buffer放入字符: '{char}'")
        
        # 创建一个Consumer，设置较高的频率以便快速测试
        consumer = Consumer(test_buffer, get_freq=1)
        
        # 初始时Buffer应该有3个元素
        self.assertEqual(test_buffer.data.qsize(), 3)
        print(f"初始状态: Buffer中有 {test_buffer.data.qsize()} 个元素")
        
        # 调用get方法3次
        results = []
        for i in range(3):
            char = consumer.get()
            print(f"第{i+1}次get: 获取字符 '{char}', Buffer剩余: {test_buffer.data.qsize()}")
            results.append(char)
        
        # 验证Buffer现在应该为空
        self.assertTrue(test_buffer.data.empty())
        print("验证完成: Buffer现在为空")
        
        # 验证获取的元素都是单个字符
        for i, char in enumerate(results):
            print(f"验证第{i+1}个获取的字符 '{char}' 是否为单字符")
            self.assertIsInstance(char, str)
            self.assertEqual(len(char), 1)
    
    def test_consumer_frequency(self):
        """测试Consumer的get频率是否正确"""
        print("\n===== 测试Consumer的get频率 =====")
        test_buffer = Buffer(size=10)
        
        # 先向buffer中放入一些元素
        for i in range(3):
            char = random.choice(string.ascii_letters + string.digits)
            test_buffer.put(char)
            print(f"向Buffer放入字符: '{char}'")
        
        # 创建一个频率为2Hz的Consumer（每0.5秒执行一次）
        consumer = Consumer(test_buffer, get_freq=2)
        print("创建Consumer，get频率: 2Hz (每0.5秒一次)")
        
        # 记录开始时间
        start_time = time.time()
        print(f"开始时间: {start_time:.3f}")
        
        # 执行2次get操作
        char1 = consumer.get()
        print(f"第1次get: 获取字符 '{char1}', 时间: {time.time():.3f}")
        char2 = consumer.get()
        print(f"第2次get: 获取字符 '{char2}', 时间: {time.time():.3f}")
        
        # 计算经过的时间
        elapsed_time = time.time() - start_time
        print(f"总耗时: {elapsed_time:.3f}秒")
        
        # 验证经过的时间约为1秒（允许有小误差）
        self.assertAlmostEqual(elapsed_time, 1, delta=0.1)
        print(f"验证完成: 耗时接近1秒，实际为{elapsed_time:.3f}秒")
    
    def test_consumer_move(self):
        """测试Consumer的move方法是否能正常从一个Buffer移动元素到另一个Buffer"""
        print("\n===== 测试Consumer的move方法 =====")
        # 创建两个Buffer，一个作为源，一个作为目标
        source_buffer = Buffer(size=5)
        dest_buffer = Buffer(size=5)
        print("创建源Buffer和目标Buffer，大小均为5")
        
        # 向源Buffer中放入3个元素
        test_chars = []
        for i in range(3):
            char = random.choice(string.ascii_letters + string.digits)
            test_chars.append(char)
            source_buffer.put(char)
            print(f"向源Buffer放入字符: '{char}'")
        
        # 创建一个Consumer
        consumer = Consumer(dest_buffer, move_freq=1)
        print("创建Consumer，move频率: 1Hz")
        
        # 初始时，源Buffer有3个元素，目标Buffer为空
        self.assertEqual(source_buffer.data.qsize(), 3)
        self.assertTrue(dest_buffer.data.empty())
        print(f"初始状态: 源Buffer有 {source_buffer.data.qsize()} 个元素, 目标Buffer为空")
        
        # 调用move方法3次
        for i in range(3):
            char = consumer.move(source_buffer)
            print(f"第{i+1}次move: 移动字符 '{char}' 从源Buffer到目标Buffer")
            print(f"  - 源Buffer剩余: {source_buffer.data.qsize()}, 目标Buffer大小: {dest_buffer.data.qsize()}")
        
        # 验证源Buffer现在应该为空
        self.assertTrue(source_buffer.data.empty())
        print("验证完成: 源Buffer现在为空")
        
        # 验证目标Buffer现在应该有3个元素
        self.assertEqual(dest_buffer.data.qsize(), 3)
        print(f"验证完成: 目标Buffer有 {dest_buffer.data.qsize()} 个元素")
        
        # 从目标Buffer获取元素，并验证它们是否匹配之前添加的字符（顺序应该相同）
        result_chars = []
        for i in range(3):
            char = dest_buffer.get()
            print(f"从目标Buffer获取第{i+1}个字符: '{char}'")
            result_chars.append(char)
        
        # 验证移动的元素与添加的元素相同（考虑队列的FIFO特性）
        self.assertEqual(test_chars, result_chars)
        print("验证完成: 移动的元素与添加的元素顺序一致")


if __name__ == '__main__':
    unittest.main()