# coding:utf-8
import Queue
from wowSocket import ConnWowSrv
from wuaiwow import app, logger


class SocksPool(object):
    def __init__(self, sock_size=0):
        self.queue = Queue.Queue(maxsize=0)
        sz = sock_size if sock_size > 0 else app.config['SOCKSPOOL_SIZE']
        for i in xrange(sz):
            self.put(ConnWowSrv())

    def empty(self):
        return self.queue.empty()

    def put(self, item, block=True, timeout=None):
        logger.info('Put sock into queue again')
        item.close()
        self.queue.put(item=item, block=block, timeout=timeout)

    def get(self, block=True, timeout=None):
        try:
            # If `False`, the program is not blocked. `Queue.Empty` is thrown if
            # the queue is empty
            s = self.queue.get(False)
        except Queue.Empty:
            s = ConnWowSrv()

        return s


socksPool = SocksPool()
