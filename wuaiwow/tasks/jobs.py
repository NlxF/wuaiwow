# coding: utf-8
import json
from wuaiwow.utils.socketConnect.socksPool import socksPool
from wuaiwow.utils.socketConnect.wowSocket import WowSocketException, assembly_request as _assembly_request
from wuaiwow.utils.playersHelper import update_wowaccount, update_wowaccount_characters
from wuaiwow import celery, db, logger
from wuaiwow.models import TaskResult

wait_for_response_time_out = 3


tasksDict = dict()   # for update character and mapping task with task name


def retry_delay(ts):
    """
        返回下次重发的时间间隔, 间隔为3/45/225/, #, 单位:分钟
    """
    return 3 * 5 ** ts      # * 60


def _error_handler(e):
    if e.err_code == 51:
        return False, u'网络不可达'
    elif e.err_code == 22:
        return False, u'参数错误'
    elif e.err_code == 61:
        return False, u'连接被拒'
    elif e.err_code == 54:
        return False, u'连接断开'
    return False, e.err_msg


class JobTask(celery.Task):
    """
        继承的Task类,用来定义成功或者失败时的动作
    """

    def on_success(self, retval, task_id, args, kwargs):
        logger.info("task success")
        task = TaskResult.query.filter(TaskResult.task_id == task_id).first()
        if task:
            task.status = True
            db.session.add(task)
            db.session.commit()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error("task failed")   # , exc:{0}, args:{1}, kwargs:{2}".format(exc, args, kwargs))
        if isinstance(exc, WowSocketException):
            task = TaskResult(task_id=task_id,
                              task_name=self.name,
                              args=json.dumps(args),
                              kwargs=json.dumps(kwargs),
                              err_code=exc.err_code,
                              exc_msg=exc.err_msg)
            db.session.add(task)
            db.session.commit()


# @celery.task(bind=True, max_retries=1)
def create_account(username, password):
    """
    创建wow账号但是没有激活,

    # @param self 绑定为当前对象
    @param username 新建账户名
    @param password 新账户密码
    """

    rst = (False, u"发送命令格式错误")
    sock = socksPool.get()
    try:
        cmd = [[{'op': '1'}, {'name': username}, {'pwd': password}],
               [{'op': '2'}, {'name': username}]]
        json_data = _assembly_request(cmd)
        if json_data is not None and sock:
            sock.send_command(json_data)
            response = sock.receive_data(5)
            dict_resp = json.loads(response)
            rst = dict_resp['isopok'], dict_resp['message']
    except Exception as exc:
        rst = (False, exc.message)
    finally:
        socksPool.put(sock)
        return rst


@celery.task(bind=True, max_retries=1)
def delete_account(self, username):
    """
    删除指定账号

    @param self 绑定为当前对象
    @param username 要删除的账号名
    """
    try:
        sock = socksPool.get()

        cmd = [[{'op': '3'}, {'name': username}]]
        # cmd = [FIRST['account'], SECOND['account']['delete'], username]
        json_data = _assembly_request(cmd)
        if json_data is not None:
            sock.send_command(json_data)
            return True, 'OK'

        socksPool.put(sock)
        return False, u"发送命令格式错误"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=retry_delay(self.request.retries))


@celery.task(bind=True, max_retries=2)
def active_account(self, username):
    """
    激活wow账号

    @param self 绑定为当前对象
    @param username 要激活的账户名
    """
    try:
        sock = socksPool.get()

        cmd = [[{'op': '4'}, {'name': username}]]
        # cmd = [FIRST['unban'], SECOND['unban']['account'], username]
        json_data = _assembly_request(cmd)
        if json_data is not None:
            sock.send_command(json_data)
            return True, 'OK'

        socksPool.put(sock)
        return False, u"发送命令格式错误"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=retry_delay(self.request.retries))


@celery.task(bind=True, max_retries=1)
def change_pwd(self, username, password):
    """
    修改密码

    @param self 绑定为当前对象
    @param username 要修改密码的账户名
    @param password 新密码
    """
    try:
        sock = socksPool.get()

        cmd = [[{'op': '5'}, {'name': username}, {'pwd': password}]]
        # cmd = [FIRST['account'], SECOND['account']['set'], THIRD['set']['password'], username, password, password]
        json_data = _assembly_request(cmd)
        if json_data is not None:
            sock.send_command(json_data)
            return True, 'OK'

        socksPool.put(sock)
        return False, u"发送命令格式错误"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=retry_delay(self.request.retries))


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
        # cmd = [FIRST['lookup'], SECOND['lookup']['player'], THIRD['player']['account'], 'abc']  # account]
        json_data = _assembly_request(cmd)
        if json_data is not None:
            sock.send_command(json_data)
            recv_data = sock.receive_data(timeout_in_seconds=wait_for_response_time_out)
            return True, recv_data

        socksPool.put(sock)
        return False, u"发送命令格式错误"
    except WowSocketException, e:
        return _error_handler(e)
    except Exception, e:
        return False, e.message


def query_characters(guid):
    """
    查询角色信息

    @param guid int 角色名的guid
    @return 角色信息
    """
    try:
        sock = socksPool.get()

        cmd = [[{'op': '7'}, {'name': str(guid)}]]
        # cmd = [FIRST['pinfo'], str(guid)]
        json_data = _assembly_request(cmd)
        if json_data is not None:
            sock.send_command(json_data)
            recv_data = sock.receive_data(timeout_in_seconds=wait_for_response_time_out)
            return True, recv_data

        socksPool.put(sock)
        return False, u"发送命令格式错误"
    except WowSocketException, e:
        return _error_handler(e)
    except Exception, e:
        return False, e.message


@celery.task(bind=True)
def level_character(self, name, level):
    """
    提升角色等级

    @param self 绑定为当前对象
    @param name 角色名
    @param level 提升的等级
    """
    try:
        sock = socksPool.get()

        cmd = [[{'op': '8'}, {'name': name}, {'level': str(level)}]]
        # cmd = [FIRST['character'], SECOND['character']['level'], name, str(level)]
        json_data = _assembly_request(cmd)
        if json_data is not None:
            sock.send_command(json_data)
            return True, 'OK'

        socksPool.put(sock)
        return False, u"发送命令格式错误"
    except WowSocketException, e:
        return False, e.err_msg


@celery.task(bind=True)
def change_gender(self, name):
    """
    自定义角色,主要是更改性别

    @param self 绑定为当前对象
    @param name 角色名
    """
    try:
        sock = socksPool.get()

        cmd = [[{'op': '9'}, {'name': name}]]
        # cmd = [FIRST['character'], SECOND['character']['customize'], name]
        json_data = _assembly_request(cmd)
        if json_data is not None:
            sock.send_command(json_data)
            return True, 'OK'

        socksPool.put(sock)
        return False, u"发送命令格式错误"
    except WowSocketException, e:
        return False, e.err_msg


@celery.task(bind=True)
def change_race(self, name):
    """
    更换种族,(同一阵营的)

    @param self 绑定为当前对象
    @param name 角色名
    """
    try:
        sock = socksPool.get()

        cmd = [[{'op': '10'}, {'name': name}]]
        # cmd = [FIRST['character'], SECOND['character']['changerace'], name]
        json_data = _assembly_request(cmd)
        if json_data is not None:
            sock.send_command(json_data)
            return True, 'OK'

        socksPool.put(sock)
        return False, u"发送命令格式错误"
    except WowSocketException, e:
        return False, e.err_msg


@celery.task(bind=True, max_retries=1)
def send_money(self, name, subject, text, money):
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
        # cmd = [FIRST['send'], SECOND['send']['money'], name, '\"'+subject+'\"', '\"'+text+'\"', money]
        json_data = _assembly_request(cmd)
        if json_data is not None:
            sock.send_command(json_data)
            return True, 'OK'

        socksPool.put(sock)
        return False, u"发送命令格式错误"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=retry_delay(self.request.retries))


@celery.task(bind=True)
def update_account_by_name(self, username):
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


@celery.task(bind=True, max_retries=3)
def update_permission_table(self, command_list):
    """
    更新game server端的permission表

    @param self 绑定为当前对象
    @param command_list 命令数组, 为[(value1, role1, label1),...]
    """
    try:
        sock = socksPool.get()

        cmd = [[{'op': '13'}, {'role': str(l[1])}, {'label': l[2]}, {'value': str(l[0])}] for l in command_list if isinstance(l, tuple) and len(l) == 3]

        json_data = _assembly_request(cmd)
        if json_data is not None:
            sock.send_command(json_data)
            return True, 'OK'

        socksPool.put(sock)
        return False, u"发送命令格式错误"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=retry_delay(self.request.retries))


@celery.task(max_retries=0, name='update-account-permission', base=JobTask)  # max_retries 为尝试的次数，不包括首次
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

        if json_data is not None:
            logger.info('ready to send json data')
            count = sock.send_command(json_data)
            logger.info('send {0} bytes data'.format(count))
            if count > 0:
                rst = True

        socksPool.put(sock)
        return rst
    except WowSocketException as exc:
        socksPool.put(sock)
        logger.error('{0} raise a exception: {1}, try again'.format(update_account_permission.name, exc.err_msg))
        raise update_account_permission.retry(exc=exc, countdown=retry_delay(update_account_permission.request.retries))


