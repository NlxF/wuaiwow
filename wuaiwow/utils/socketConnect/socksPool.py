# coding:utf-8
import Queue
from wowSocket import ConnWowSrv, result_handler
from wuaiwow import app, logger



class SocksPool(object):
    def __init__(self, sock_size=0):
        self.queue = Queue.Queue(maxsize=0)
        sz = sock_size if sock_size > 0 else app.config['SOCKSPOOL_SIZE']
        for i in xrange(sz):
            self.put(ConnWowSrv())

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(SocksPool, cls)
            cls._instance = orig.__new__(cls, *args, **kwargs)
        return cls._instance

    def empty(self):
        return self.queue.empty()

    def put(self, item, block=True, timeout=None):
        # if not item.broken:
        #     logger.info('Put sock(%d) into queue(%d).' % (item.sock.fileno(), id(self.queue)))
        #     item.connected = False
        #     self.queue.put(item=item, block=block, timeout=timeout)
        # else:
        #     item.close()
        #     del item
        item.close()
        del item

    def get(self, block=True, timeout=None):
        try:
            # If `False`, the program is not blocked.
            # `Queue.Empty` is thrown if the queue is empty
            s = self.queue.get(False)
            logger.info("get sock(%d) in queue(%d)." % (s.sock.fileno(), id(self.queue)))
        except Queue.Empty:
            s = ConnWowSrv()
            logger.info("get new sock(%d)." % s.sock.fileno())

        return s

    def __del__(self):
        logger.info('socksPool deleting.')


socksPool = SocksPool()