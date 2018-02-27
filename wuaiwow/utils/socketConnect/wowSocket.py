# coding:utf-8
import json
from sys import platform
import select
import socket
import errno
import tea
import crc8
from wuaiwow import app, logger


class wowSocketExceptionType:
    wowSocketExceptSocket      = -1  # socket错误
    wowSocketExceptUnIntegrity = -2  # 数据不完整
    wowSocketExceptUnknown     = 0


class WowSocketException(Exception):
    """sock异常类

    err_code: -1
    """
    def __init__(self, err_code, err_msg):
        self.err_code = err_code
        self.err_msg = err_msg

    def __str__(self):
        return "error code: {errCode}, error message: {msg}".format(errCode=self.err_code, msg=self.err_msg)

    def __repr__(self):
        return "error code: {errCode}, error message: {msg}".format(errCode=self.err_code, msg=self.err_msg)


def assembly_request(cmds):
    """ 返回请求字符串

    @param cmds:commands命令
    @return 请求字符串
    """

    vals = []
    keys = []
    for cmd in cmds:
        t1 = {}
        t2 = []
        [(t1.update(k), t2.extend(k.keys())) for k in cmd]
        keys.append(t2)
        vals.append(t1)

    cmd_dic = {"values": vals, "keys": keys} if len(vals) > 0 and len(keys) > 0 else None
    return json.dumps(cmd_dic)


class ConnWowSrv(object):
    """
        通信类，keepalive 连接
    """
    def __init__(self, port=None, host=None, family=socket.AF_INET, sock_type=socket.SOCK_STREAM):
        self.host = host if host else app.config['LSERVER_HOST']
        self.port = port if port else app.config['LSERVER_PORT']
        self.tea = tea.Tea() if app.config['NEEDENCRYPTION'] else None
        self.crc8 = crc8.crc8()
        self.sock = socket.socket(family=family, type=sock_type)
        self.connected = False

    def set_keepalive(self, after_idle_sec=1, interval_sec=3, max_fails=5):
        """Set TCP keepalive on an open socket.

        It activates after 1 second (after_idle_sec) of idleness,
        then sends a keepalive ping once every 3 seconds (interval_sec),
        and closes the connection after 5 failed ping (max_fails), or 15 seconds
        """
        if platform == "linux" or platform == "linux2":
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            # overrides value (in seconds) shown by sysctl net.ipv4.tcp_keepalive_time
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
            # overrides value shown by sysctl net.ipv4.tcp_keepalive_intvl
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
            # overrides value shown by sysctl net.ipv4.tcp_keepalive_probes
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)
        else:
            # osx or windows
            TCP_KEEPALIVE = 0x10
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.sock.setsockopt(socket.IPPROTO_TCP, TCP_KEEPALIVE, interval_sec)

    def connect_to(self):
        if not self.connected:
            logger.info('settimeout')
            self.sock.settimeout(10)                                   # 连接超时时间
            # self.set_keepalive()                                     # keepalive
            logger.info('connecting...')
            self.sock.connect((self.host, self.port))
            self.connected = True
            # try:
            #     self.sock.settimeout(10)                                   # 连接超时时间
            #     # self.set_keepalive()                                     # keepalive
            #     self.sock.connect((self.host, self.port))
            # except socket.error, e:
            #     raise WowSocketException(err_code=e.errno, err_msg=e.message)
            # else:
            #     self.connected = True

    def _to_bytes(self, num, length, endianess='big'):
        try:
            h = '%x' % num
            s = ('0' * (len(h) % 2) + h).zfill(length * 2).decode('hex')
            return s if endianess == 'big' else s[::-1]
        except:
            return '00'

    def _to_int(self, buf, length):
        value = 0
        try:
            for i in range(length):
                bit = ord(buf[i])
                if bit > 255 or bit < 0:
                    value = 0
                    break
                value = value * 256 + bit
        except:
            pass
        return value

    def send_command(self, data):
        try:
            self.connect_to()
            logger.info('connect to remote server success')

            if isinstance(data, unicode):
                data = str(data).strip()
            encode = self.tea.encrypt(data) if self.tea else data
            crc_data = self.crc8.crc8_data(encode)
            with_head = self._to_bytes(len(crc_data), app.config['PACKAGE_HEAD_SIZE']) + crc_data    # 加上head byte
            count = self.sock.sendall(with_head)
            return count
        except socket.error, e:
            logger.error('socket error. exception: {0}'.format(e))
            raise WowSocketException(err_code=wowSocketExceptionType.wowSocketExceptSocket, err_msg=e.message)
        except Exception, e:
            logger.error('send command raise unknown exception:{0}'.format(e.message))
            raise WowSocketException(err_code=wowSocketExceptionType.wowSocketExceptUnknown, err_msg=e.message)

    def _recv_n(self, count):
        data = b''
        while len(data) < count:
            packet = self.sock.recv(count - len(data))
            if not packet:
                return None
            data += packet
        return data

    def receive_data(self, timeout_in_seconds=1):
        """等待timeout_in_seconds秒or超时

        @param timeout_in_seconds 等待的秒数
        @return 无
        """
        try:
            self.connect_to()

            self.sock.setblocking(0)
            ready = select.select([self.sock], [], [], timeout_in_seconds)
            if ready[0]:
                head_size = app.config['PACKAGE_HEAD_SIZE']
                buf = self.sock.recv(head_size, socket.MSG_PEEK)
                n_read = self._to_int(buf, head_size)
                receive = self._recv_n(n_read + head_size)[head_size:]
                # receive = self.sock.recv(1024*2)
                if self.crc8.is_data_integrity(receive):
                    reverse_data = self.crc8.reverse_crc8_data(receive)
                    decrypt_data = self.tea.decrypt(reverse_data) if self.tea else reverse_data
                    return decrypt_data
                else:
                    raise WowSocketException(err_code=wowSocketExceptionType.wowSocketExceptUnIntegrity,
                                             err_msg=u"数据不完整")
        except socket.error, e:
            logger.error('Failed to recv data. Error code: ' + str(e.errno) + ', Error message : ' + e.message)
            raise WowSocketException(err_code=wowSocketExceptionType.wowSocketExceptSocket, err_msg=e.message)
        except Exception, e:
            logger.error('receive data raise exception:{0}'.format(e.message))
            raise WowSocketException(err_code=wowSocketExceptionType.wowSocketExceptUnknown, err_msg=e.message)

    def close(self):
        if self.connected:
            self.sock.close()
            self.connected = False


# wowSocket = ConnWowSrv(port=8009)
# import sys
# sys.modules[__name__] = ConnWowSrv(port=8009)


if __name__ == '__main__':
    a = ConnWowSrv(port=8009)
    a.send_command('WOW1.1')
