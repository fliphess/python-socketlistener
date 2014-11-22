import time


class SocketInputQueue(list):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(SocketInputQueue, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def add(self, event):
        self.append(event)

    def get(self):
        try:
            return self.pop(0)
        except IndexError:
            return False

    def flush(self):
        self[:] = []

    def generator(self, wait_time=0.1):
        while 1:
            task = self.get()
            if task:
                yield task
                continue
            time.sleep(wait_time)


class SocketEvent(dict):
    def __init__(self, **kwargs):
        super(SocketEvent, self).__init__()
        self.update(kwargs)


queue = SocketInputQueue()