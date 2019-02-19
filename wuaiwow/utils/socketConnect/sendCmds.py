# # coding: utf-8
# import json
# from socksPool import socksPool
# from wowSocket import WowSocketException, assembly_json as _assembly_json
# from wuaiwow.socketConnect.commands import FIRST, SECOND, THIRD
# from wuaiwow import celery
#
#
# @celery.task()
# def create_account(username, password):
#     """
#     创建wow账号但是没有激活
#
#     @param username 新建账户名
#     @param password 新账户密码
#     """
#     try:
#         sock = socksPool.get()
#         cmd = [FIRST['account'], SECOND['account']['create'], username, password]
#         json_data = json.dumps(_assembly_json(cmd))
#         sock.send_command(json_data)
#         cmd = [FIRST['ban'], SECOND['ban']['account'], username, '4d20h3s', 'INIT']
#         json_data = json.dumps(_assembly_json(cmd))
#         sock.send_command(json_data)
#         socksPool.put(sock)
#         return True, 'OK'
#     except WowSocketException, e:
#         return False, e.err_msg
#         # raise WowSocketException(wowSocketExceptionType.wowSocketExceptTimeOut, e.message)
#
#
# @celery.task()
# def delete_account(username):
#     """
#     删除指定账号
#
#     @param username 要删除的账号名
#     """
#     try:
#         sock = socksPool.get()
#         cmd = [FIRST['account'], SECOND['account']['delete'], username]
#         json_data = json.dumps(_assembly_json(cmd))
#         sock.send_command(json_data)
#         socksPool.put(sock)
#         return True, 'OK'
#     except WowSocketException, e:
#         return False, e.err_msg
#
#
# @celery.task()
# def active_account(username):
#     """
#     激活wow账号
#
#     @param username 要激活的账户名
#     """
#     try:
#         sock = socksPool.get()
#         cmd = [FIRST['unban'], SECOND['unban']['account'], username]
#         json_data = json.dumps(_assembly_json(cmd))
#         sock.send_command(json_data)
#         socksPool.put(sock)
#         return True, 'OK'
#     except WowSocketException, e:
#         return False, e.err_msg
#
#
# @celery.task()
# def change_pwd(username, password):
#     """
#     修改密码
#
#     @param username 要修改密码的账户名
#     @param password 新密码
#     """
#     try:
#         sock = socksPool.get()
#         cmd = [FIRST['account'], SECOND['account']['set'], THIRD['set']['password'], username, password, password]
#         json_data = json.dumps(_assembly_json(cmd))
#         sock.send_command(json_data)
#         socksPool.put(sock)
#         return True, 'OK'
#     except WowSocketException, e:
#         return False, e.err_msg
#
#
# @celery.task()
# def query_account(account):
#     """
#     查询账号信息
#
#     @param account 账号名
#     @return 账号下所有角色名,返回格式:
#     "Characters at account ABC (Id: 10)
#        wyyzxml (GUID 0)
#        wyyzxml2 (GUID 1)"
#
#     """
#     try:
#         sock = socksPool.get()
#         cmd = [FIRST['lookup'], SECOND['lookup']['player'], THIRD['player']['account'], 'abc']  # account]
#         json_data = json.dumps(_assembly_json(cmd, flag=1))
#         sock.send_command(json_data)
#         recv_data = sock.receive_data(timeout_in_seconds=2)
#         socksPool.put(sock)
#         return True, recv_data
#     except WowSocketException, e:
#         return False, e.err_msg
#
#
# @celery.task()
# def query_characters(guid):
#     """
#     查询角色信息
#
#     @param guid int 角色名的guid
#     @return 角色信息
#     """
#     try:
#         sock = socksPool.get()
#         cmd = [FIRST['pinfo'], str(guid)]
#         json_data = json.dumps(_assembly_json(cmd, flag=1))
#         sock.send_command(json_data)
#         recv_data = sock.receive_data(timeout_in_seconds=2)
#         socksPool.put(sock)
#         return True, recv_data
#     except WowSocketException, e:
#         return False, e.err_msg
#
#
# @celery.task()
# def level_character(name, level):
#     """ 提升角色等级
#     @param name 角色名
#     @param level 提升的等级
#     """
#     try:
#         sock = socksPool.get()
#         cmd = [FIRST['character'], SECOND['character']['level'], name, str(level)]
#         json_data = json.dumps(_assembly_json(cmd))
#         sock.send_command(json_data)
#         socksPool.put(sock)
#         return True, 'OK'
#     except WowSocketException, e:
#         return False, e.err_msg
#
#
# @celery.task()
# def change_gender(name):
#     """ 自定义角色,主要是更改性别
#     @param name 角色名
#     """
#     try:
#         sock = socksPool.get()
#         cmd = [FIRST['character'], SECOND['character']['customize'], name]
#         json_data = json.dumps(_assembly_json(cmd))
#         sock.send_command(json_data)
#         socksPool.put(sock)
#         return True, 'OK'
#     except WowSocketException, e:
#         return False, e.err_msg
#
#
# @celery.task()
# def change_race(name):
#     """ 更换种族,(同一阵营的)
#     @param name 角色名
#     """
#     try:
#         sock = socksPool.get()
#         cmd = [FIRST['character'], SECOND['character']['changerace'], name]
#         json_data = json.dumps(_assembly_json(cmd))
#         sock.send_command(json_data)
#         socksPool.put(sock)
#         return True, 'OK'
#     except WowSocketException, e:
#         return False, e.err_msg
#
#
# @celery.task()
# def send_money(name, subject, text, money):
#     """ 以邮件形式送钱
#     @param name 角色名
#     @param subject 邮件主题
#     @param text 邮件正文
#     @param money 存在于附件中的money
#     """
#     try:
#         sock = socksPool.get()
#         cmd = [FIRST['send'], SECOND['send']['money'], name, '\"'+subject+'\"', '\"'+text+'\"', money]
#         json_data = json.dumps(_assembly_json(cmd))
#         sock.send_command(json_data)
#         socksPool.put(sock)
#         return True, 'OK'
#     except WowSocketException, e:
#         return False, e.err_msg