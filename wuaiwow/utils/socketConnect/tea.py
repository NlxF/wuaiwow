# # coding:utf-8
# pypy use TEA complex
# from ctypes import *
# # from boostpy import TEA
#
#
# class Tea(object):
#     """tea encrypt"""
#
#     def __init__(self, loop=16, key=None):
#         """init Tea object
#
#         @param loop: default is 16
#         @param key: default is *******
#         """
#         self.tea = TEA(loop, key) if key else TEA(loop)
#
#     def _group(self, seq, size):
#         while seq:
#             yield seq[:size]
#             seq = seq[size:]
#
#     def encrypt(self, content):
#         # encrypt content
#         encode = ""
#         _input = create_string_buffer(8)
#         str_list = list(self._group(content, 8))
#         for aStr in str_list:
#             _input.value = aStr
#             encode += self.tea.encrypt(_input.value)
#
#         with open(r"/var/tmp/log.txt", 'w+') as f:
#             f.write(encode)
#         return encode
#
#     def decrypt(self, encode):
#         # decrypt content
#         decode = ""
#         str_list = list(self._group(encode, 8))
#         for aStr in str_list:
#             decode += self.tea.decrypt(aStr).strip('\x00')
#
#         with open(r"/var/tmp/log2.txt", 'w+') as f:
#             f.write(decode)
#         return decode
#
#
# if __name__ == "__main__":
#     t = Tea()
#     num = 1
#     s = "HELLO WORLD"
#     # encode = t.encrypt(s)
#
#     for i in xrange(1000):
#         import random
#         s = random.sample('zyxwvutsrqponmlkjihgfedcba _~!@#$%^&*()+=-1234567890', 40)
#         s2 = ''.join(s)
#         s2.strip()
#         # s2 = 'unban account ism5'
#         s3 = t.decrypt(t.encrypt(s2))
#         if s3 != s2:
#             print num," before:", s2, "after:", s3
#             num += 1
