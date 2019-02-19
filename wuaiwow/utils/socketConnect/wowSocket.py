# -*-coding:utf-8-*-
import json
from sys import platform
import select
import socket
# import tea
import crc8
from flask_user.translations import gettext as _
from wuaiwow import app, logger


def result_handler(rst):
    if isinstance(rst, socket.error):
        err = rst
        if isinstance(err, socket.timeout):
            msg = err[-1]
        else:
            if err.errno == 10053:
                msg = 'An established connection was aborted by the software in your host machine'
            elif err.errno == 10061:
                msg = 'Connection refused'
            else:
                msg = u'未知'
            msg = u"{0}:{1}".format(err.errno, msg)
        return False, msg
    elif isinstance(rst, ValueError):
        err = rst
        return False, err.message
    elif isinstance(rst, Exception):
        err = rst
        return False, err.message
    elif isinstance(rst, dict):
        if rst.has_key('isopok') and rst.has_key('message'):
            return rst['isopok'], rst['message']
        else:
            return False, u'未知消息'
    elif isinstance(rst, int):
        if rst == 1:
            return False, u"发送命令格式错误"
        elif rst == 2:
            return False, u"incomplete data"
    else:
        return False, u"未知错误"


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

    cmd_dic = {"values": vals, "keys": keys}
    return json.dumps(cmd_dic) if len(vals) > 0 and len(keys) > 0 else None


class ConnWowSrv(object):
    """
        通信类，keepalive 连接
    """
    def __init__(self, port=None, host=None, family=socket.AF_INET, sock_type=socket.SOCK_STREAM):
        self.host = host if host else app.config['LSERVER_HOST']
        self.port = port if port else app.config['LSERVER_PORT']
        self.tea = None  # tea.Tea() if app.config['NEEDENCRYPTION'] else None
        self.crc8 = crc8.crc8()
        self.sock = socket.socket(family=family, type=sock_type)
        self.connected = False
        self.broken = False

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
        rtn = True, 'ok'
        if not self.connected:
            logger.info('connecting LServer...')
            try:
                self.sock.settimeout(5)                                  # 连接超时时间
                self.set_keepalive()                                     # keepalive
                self.sock.connect((self.host, self.port))
            except Exception as e:
                self.connected = False
                self.broken = True
                rtn = result_handler(e)
            else:
                self.connected = True
                self.broken = False
                rtn = True, 'ok'
        return rtn

    def send_command(self, data):
        try:
            rst, msg = self.connect_to()
            if not rst:
                logger.error(u'connect to LServer failed({0})'.format(msg))
                return 0, _('Connect to LServer failed, try later.')

            logger.info('connect to LServer success')
            if isinstance(data, unicode):
                data = str(data).strip()
            encode = self.tea.encrypt(data) if self.tea else data
            crc_data = self.crc8.crc8_data(encode)
            with_head = self._to_bytes(len(crc_data), app.config['PACKAGE_HEAD_SIZE']) + crc_data    # 加上head byte
            count = self.sock.sendall(with_head)
            return True, 'OK'
        except Exception as e:
            rst, msg = result_handler(e)
            logger.error('send command exception:{0}'.format(msg))
            self.broken = True
            return 0, msg

    def receive_data(self, timeout_in_seconds=1):
        """等待timeout_in_seconds秒 or 超时

        @param timeout_in_seconds 等待的秒数
        @return (status, message)
        """
        try:
            if not self.connected:
                return False, "not connected with LServer."

            self.sock.setblocking(0)
            ready = select.select([self.sock], [], [], timeout_in_seconds)
            if ready[0]:
                head_size = app.config['PACKAGE_HEAD_SIZE']
                buf = self.sock.recv(head_size, socket.MSG_PEEK)
                n_read = self._to_int(buf, head_size)
                receive = self._recv_n(n_read + head_size)[head_size:]
                if self.crc8.is_data_integrity(receive):
                    reverse_data = self.crc8.reverse_crc8_data(receive)
                    decrypt_data = self.tea.decrypt(reverse_data) if self.tea else reverse_data
                    return True, decrypt_data
                else:
                    return result_handler(2)
            else:
                return False, 'recv data timeout'
        except Exception, e:
            rst, msg = result_handler(e)
            # logger.error('receive data raise exception:{0}'.format(msg))
            self.broken = True
            return False, msg

    def close(self):
        if self.connected:
            self.sock.close()
            self.connected = False

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

    def _recv_n(self, count):
        data = b''
        while len(data) < count:
            packet = self.sock.recv(count - len(data))
            if not packet:
                return None
            data += packet
        return data

    def __del__(self):
        logger.info('sock fileno:%d is deleting' % self.sock.fileno())


# wowSocket = ConnWowSrv(port=8009)
# import sys
# sys.modules[__name__] = ConnWowSrv(port=8009)


if __name__ == '__main__':
    a = ConnWowSrv(port=8009)
    a.send_command('WOW1.1')
