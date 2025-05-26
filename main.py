import threading
import multiprocessing
import os
import buffer

size_buffer1 = 8
size_buffer2 = 8
size_buffer3 = 8

put_freq = 2
c1_get_freq = 2
c2_get_freq = 2
c1_move_freq = 2
c2_move_freq = 2


buffer1 = buffer.Buffer(size_buffer1)
buffer2 = buffer.Buffer(size_buffer2)
buffer3 = buffer.Buffer(size_buffer3)

p = buffer.Producer(buffer1,put_freq)
c1 = buffer.Consumer(buffer2,c1_get_freq,c1_move_freq)
c2 = buffer.Consumer(buffer3,c2_get_freq,c2_move_freq)