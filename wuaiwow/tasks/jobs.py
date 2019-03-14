# coding:utf-8
import json
from flask import url_for, current_app
from flask_user import emails
from wuaiwow.utils.socketConnect.socksPool import socksPool, result_handler as _result_handler
from wuaiwow.utils.socketConnect.wowSocket import assembly_request as _assembly_request
from wuaiwow.utils.playersHelper import update_wowaccount, update_wowaccount_characters
# from wuaiwow import celery, db, celery_logger, logger
from wuaiwow.models import TaskResult

wait_for_response_time_out = 3


tasksDict = dict()   # for update character and mapping task with task name


def retry_delay(ts):
    """
        返回下次重发的时间间隔, 间隔为3/45/225/, #, 单位:分钟
    """
    return 3 * 5 ** ts      # * 60


# class JobTask(celery.Task):
#     """
#         继承的Task类,用来定义成功或者失败时的动作
#     """
#
#     def on_success(self, retval, task_id, args, kwargs):
#         celery_logger.info("task success")
#         task = TaskResult.query.filter(TaskResult.task_id == task_id).first()
#         if task:
#             task.status = True
#             db.session.add(task)
#             db.session.commit()
#
#     def on_failure(self, exc, task_id, args, kwargs, einfo):
#         celery_logger.error("task failed")   # , exc:{0}, args:{1}, kwargs:{2}".format(exc, args, kwargs))
#         if isinstance(exc, Exception):
#             task = TaskResult(task_id=task_id,
#                               task_name=self.name,
#                               args=json.dumps(args),
#                               kwargs=json.dumps(kwargs),
#                               err_code=exc.errno,
#                               exc_msg=exc.message)
#             db.session.add(task)
#             db.session.commit()


# @celery.task(base=JobTask, max_retries=1)
def create_account(username, password):
    """
    创建wow账号但是没有激活,

    # @param self 绑定为当前对象
    @param username 新建账户名
    @param password 新账户密码
    """

    try:
        sock = socksPool.get()

        cmd = [[{'op': '1'}, {'name': username}, {'pwd': password}],
               [{'op': '2'}, {'name': username}]]
        json_data = _assembly_request(cmd)
        if json_data:
            rst = sock.send_command(json_data)
            if rst[0]:
                response = sock.receive_data(5)
                if response[0]:
                    dict_resp = json.loads(response[-1])
                    rst = _result_handler(dict_resp)
                else:
                    rst = response
        else:
            rst = _result_handler(1)
    except Exception as exc:
        rst = _result_handler(exc)

    socksPool.put(sock)
    return rst


# @celery.task(base=JobTask, max_retries=1)
def delete_account(username):
    """
    删除指定账号

    # @param self 绑定为当前对象
    @param username 要删除的账号名
    """
    try:
        sock = socksPool.get()

        cmd = [[{'op': '3'}, {'name': username}]]
        json_data = _assembly_request(cmd)
        if json_data:
            rst = sock.send_command(json_data)
            if rst[0]:
                response = sock.receive_data(5)
                if response[0]:
                    dict_resp = json.loads(response[-1])
                    rst = _result_handler(dict_resp)
                else:
                    rst = response
        else:
            rst = _result_handler(1)
    except Exception as exc:
        rst = _result_handler(exc)

    socksPool.put(sock)
    return rst


# @celery.task(base=JobTask, max_retries=2)
def send_registered_email(user, user_email, require_email_confirmation=True):
    try:
        user_manager = current_app.user_manager
        # Send 'confirm_email' or 'registered' email
        if user_manager.enable_email and user_manager.enable_confirm_email:
            # Generate confirm email link
            object_id = user_email.id if user_email else int(user.get_id())
            token = user_manager.generate_token(object_id)
            confirm_email_link = url_for('user.confirm_email', token=token, _external=True)

            # Send email
            emails.send_registered_email(user, user_email, confirm_email_link)

            return 'send successfully.'
    except Exception as exc:
        raise
        # raise send_registered_email.retry(exc=exc, countdown=retry_delay(send_registered_email.request.retries))

    return 'ok'


# @celery.task(base=JobTask, bind=True, max_retries=2)
def active_account(username):
    """
    激活wow账号

    @param self 绑定为当前对象
    @param username 要激活的账户名
    """
    try:
        sock = socksPool.get()

        cmd = [[{'op': '4'}, {'name': username}]]
        json_data = _assembly_request(cmd)
        if json_data:
            rst = sock.send_command(json_data)
            if rst[0]:
                response = sock.receive_data(5)
                if response[0]:
                    dict_resp = json.loads(response[-1])
                    rst = _result_handler(dict_resp)
                else:
                    rst = response
        else:
            rst = _result_handler(1)
    except Exception as exc:
        socksPool.put(sock)
        raise
        # raise self.retry(exc=exc, countdown=retry_delay(self.request.retries))

    socksPool.put(sock)
    return rst


# @celery.task(base=JobTask, bind=True, max_retries=1)
def change_pwd(username, password):
    """
    修改密码

    @param self 绑定为当前对象
    @param username 要修改密码的账户名
    @param password 新密码
    """
    try:
        sock = socksPool.get()

        cmd = [[{'op': '5'}, {'name': username}, {'pwd': password}]]
        json_data = _assembly_request(cmd)
        if json_data:
            rst = sock.send_command(json_data)
            if rst[0]:
                response = sock.receive_data(5)
                if response[0]:
                    dict_resp = json.loads(response[-1])
                    rst = _result_handler(dict_resp)
                else:
                    rst = response
        else:
            rst = _result_handler(1)
    except Exception as exc:
        socksPool.put(sock)
        raise
        # raise self.retry(exc=exc, countdown=retry_delay(self.request.retries))

    socksPool.put(sock)
    return rst


def query_account(account):
    """
    查询账号信息

    @param account 账号名
    @return 账号下所有角色名,返回格式:
    "Characters at account ABC (Id: 10)
       wyyzxml (GUID 0)
       wyyzxml2 (GUID 1)"

    """
    try:
        sock = socksPool.get()
        cmd = [[{'op': '6'}, {'name': account}]]
        json_data = _assembly_request(cmd)
        if json_data:
            rst = sock.send_command(json_data)
            if rst[0]:
                response = sock.receive_data(timeout_in_seconds=wait_for_response_time_out)
                if response[0]:
                    dict_resp = json.loads(response[-1])
                    rst = _result_handler(dict_resp)
                else:
                    rst = response
        else:
            rst = _result_handler(1)
    except Exception, e:
        rst = _result_handler(e)

    socksPool.put(sock)
    return rst


def query_characters(guid):
    """
    查询角色信息

    @param guid int 角色名的guid
    @return 角色信息
    """
    try:
        sock = socksPool.get()

        cmd = [[{'op': '7'}, {'name': str(guid)}]]
        json_data = _assembly_request(cmd)
        if json_data:
            rst = sock.send_command(json_data)
            if rst[0]:
                response = sock.receive_data(timeout_in_seconds=wait_for_response_time_out)
                if response[0]:
                    dict_resp = json.loads(response[-1])
                    rst = _result_handler(dict_resp)
                else:
                    rst = response
        else:
            rst = _result_handler(1)
    except Exception, e:
        rst = _result_handler(e)

    socksPool.put(sock)
    return rst


# @celery.task(base=JobTask, bind=True)
def level_character(name, level):
    """
    提升角色等级

    @param self 绑定为当前对象
    @param name 角色名
    @param level 提升的等级
    """
    try:
        sock = socksPool.get()
        cmd = [[{'op': '8'}, {'name': name}, {'level': str(level)}]]
        json_data = _assembly_request(cmd)
        if json_data:
            rst = sock.send_command(json_data)
            if rst[0]:
                response = sock.receive_data(timeout_in_seconds=wait_for_response_time_out)
                if response[0]:
                    dict_resp = json.loads(response[-1])
                    rst = _result_handler(dict_resp)
                else:
                    rst = response
        else:
            rst = _result_handler(1)
    except Exception as exc:
        socksPool.put(sock)
        raise
        # raise self.retry(exc=exc, countdown=retry_delay(self.request.retries))

    socksPool.put(sock)
    return rst


# @celery.task(base=JobTask, bind=True)
def change_gender(name):
    """
    自定义角色,主要是更改性别

    @param self 绑定为当前对象
    @param name 角色名
    """
    try:
        sock = socksPool.get()
        cmd = [[{'op': '9'}, {'name': name}]]
        json_data = _assembly_request(cmd)
        if json_data:
            rst = sock.send_command(json_data)
            if rst[0]:
                response = sock.receive_data(timeout_in_seconds=wait_for_response_time_out)
                if response[0]:
                    dict_resp = json.loads(response[-1])
                    rst = _result_handler(dict_resp)
                else:
                    rst = response
        else:
            rst = _result_handler(1)
    except Exception as exc:
        socksPool.put(sock)
        raise
        # raise self.retry(exc=exc, countdown=retry_delay(self.request.retries))

    socksPool.put(sock)
    return rst


# @celery.task(base=JobTask, bind=True)
def change_race(name):
    """
    更换种族,(同一阵营的)

    @param self 绑定为当前对象
    @param name 角色名
    """
    try:
        sock = socksPool.get()
        cmd = [[{'op': '10'}, {'name': name}]]
        json_data = _assembly_request(cmd)
        if json_data:
            rst = sock.send_command(json_data)
            if rst[0]:
                response = sock.receive_data(timeout_in_seconds=wait_for_response_time_out)
                if response[0]:
                    dict_resp = json.loads(response[-1])
                    rst = _result_handler(dict_resp)
                else:
                    rst = response
        else:
            rst = _result_handler(1)
    except Exception as exc:
        socksPool.put(sock)
        raise
        # raise self.retry(exc=exc, countdown=retry_delay(self.request.retries))

    socksPool.put(sock)
    return rst


# @celery.task(base=JobTask, bind=True, max_retries=1)
def send_money(name, subject, text, money):
    """
    以邮件形式送钱

    @param self 绑定为当前对象
    @param name 角色名
    @param subject 邮件主题
    @param text 邮件正文
    @param money 存在于附件中的money
    """
    try:
        sock = socksPool.get()

        cmd = [[{'op': '11'}, {'name': name, 'subject': subject, 'text': '\"'+text+'\"', 'money': '\"'+money+'\"'}]]
        json_data = _assembly_request(cmd)
        if json_data:
            rst = sock.send_command(json_data)
            if rst[0]:
                response = sock.receive_data(timeout_in_seconds=wait_for_response_time_out)
                if response[0]:
                    dict_resp = json.loads(response[-1])
                    rst = _result_handler(dict_resp)
                else:
                    rst = response
        else:
            rst = _result_handler(1)
    except Exception as exc:
        socksPool.put(sock)
        raise
        # raise self.retry(exc=exc, countdown=retry_delay(self.request.retries))

    socksPool.put(sock)
    return rst


# @celery.task(base=JobTask, bind=True)
def update_account_by_name(username):
    all_success = True
    opt, json_data = query_account(username)
    if opt:
        # update_chs = []
        characters = update_wowaccount(username, json.loads(json_data))   # fetch all characters in account
        for one in characters:
            opt, json_data = query_characters(one.guid)
            if opt:
                chs = update_wowaccount_characters(username, json.loads(json_data))
                # update_chs.append(chs)
            else:
                all_success = False

        rst = (True, u"更新账户成功" if all_success else u"账户更新不完全成功")
    else:
        print json_data
        rst = (False, u"更新账户失败:"+json_data)

    return rst


# @celery.task(base=JobTask, max_retries=0, name='update-account-permission')  # max_retries 为尝试的次数，不包括首次
def update_account_permission(command_list):
    """
    更新game server端的account-permission表

    @param command_list 命令数组, 为[(account1, value1),...]
    @return bool 同步是否成功
    """
    rst = False
    sock = socksPool.get()
    try:
        cmd = [[{'op': '12'}, {'account': l[0]}, {'value': str(l[-1])}] for l in command_list if len(l) == 2]
        json_data = _assembly_request(cmd)
        logger.info('send json data is:{0}'.format(json_data))
        if json_data:
            rst = sock.send_command(json_data)
            if rst[0]:
                logger.info('send {0} bytes data'.format(rst[0]))
                response = sock.receive_data(timeout_in_seconds=wait_for_response_time_out)
                if response[0]:
                    dict_resp = json.loads(response[-1])
                    rst = _result_handler(dict_resp)
                else:
                    rst = response
        else:
            rst = _result_handler(1)
    except Exception as exc:
        socksPool.put(sock)
        logger.error('{0} raise a exception: {1}, try again'.format(update_account_permission.name, exc.message))
        raise
        # raise update_account_permission.retry(exc=exc, countdown=retry_delay(update_account_permission.request.retries))

    socksPool.put(sock)
    return rst


# @celery.task(base=JobTask, bind=True, max_retries=3)
def update_permission_table(command_list):
    """
    更新game server端的permission表

    @param self 绑定为当前对象
    @param command_list 命令数组, 为[(value1, role1, label1),...]
    """
    try:
        sock = socksPool.get()

        cmd = [[{'op': '13'}, {'role': str(l[1])}, {'label': l[2]}, {'value': str(l[0])}] for l in command_list if isinstance(l, tuple) and len(l) == 3]

        json_data = _assembly_request(cmd)
        if json_data:
            rst = sock.send_command(json_data)
            if rst[0]:
                response = sock.receive_data(timeout_in_seconds=wait_for_response_time_out)
                if response[0]:
                    dict_resp = json.loads(response[-1])
                    rst = _result_handler(dict_resp)
                else:
                    rst = response
        else:
            rst = _result_handler(1)
    except Exception as exc:
        socksPool.put(sock)
        raise
        # raise self.retry(exc=exc, countdown=retry_delay(self.request.retries))

    socksPool.put(sock)
    return rst

