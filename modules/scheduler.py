import time
import threading

def schedule(interval, func):
    base_time = time.time()
    next_time = 0
    while True:
        t = threading.Thread(target=func)
        t.start()
        next_time = ((base_time - time.time()) % interval) or interval
        time.sleep(next_time)