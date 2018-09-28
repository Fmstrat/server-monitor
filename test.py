import threading
import time

def openThread(a):
    print("start" + str(a))
    time.sleep(a)
    print("finish" + str(a))

threads = []
t = threading.Thread(target=openThread, args=(1,))
threads.append(t)
t = threading.Thread(target=openThread, args=(2,))
threads.append(t)

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()
