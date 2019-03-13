# coding:utf-8
import json
import random
import math
import datetime
# from celery.exceptions import TimeoutError
from flask import jsonify, current_app, url_for
from flask import render_template, Blueprint, request, redirect, flash
from flask_login import logout_user
from flask_user import current_user, login_required, emails
from flask_user.translations import gettext as _
# from flask_cache import Cache
from wuaiwow.utils import add_blueprint, gen_rnd_string
from wuaiwow.utils.accountHelper import endpoint_url
from wuaiwow.utils.templateHelper import template_by_role
# from wuaiwow.utils.templateHelper import template_by_role, random_prompt
from wuaiwow.utils.modelHelper import (level_by_permission_value, time_by_level, get_permission_num,
                                       get_permission_by_role, get_permission_by_level, find_all_roles,
                                       permission_value_by_level, get_message_by_index_num)
# from wuaiwow.utils.playersHelper import (update_wowaccount, update_wowaccount_characters,
#                                          find_or_create_character)
# from wuaiwow.models import (Characters, AlivePrompt, LevelPrompt, RacePrompt,
#                             JobPrompt, GenderPrompt, MoneyPrompt, Permission)
# from wuaiwow.models import Message
from wuaiwow import tasks, app, db
# from wuaiwow.forms import PromoteForm


bp = Blueprint('player', __name__, url_prefix='/')


@bp.route('user/profile', methods=['GET', ])
@bp.route('user/account', methods=['GET', ])
@login_required
def user_account():

    gen = (msg for msg in current_user.messages if not msg.is_read)
    cnt = len(list(gen))
    template_name = template_by_role(current_user, 'custom/cms/player_profile.html',
                                                   'custom/cms/gm_profile.html',
                                                   'custom/cms/admin_profile.html')
    return render_template(template_name,
                           user=current_user,
                           unread_cnt=cnt,
                           profile='class=active')


@bp.route('user/all/message', methods=['GET', ])
@login_required
def user_message():


    template_name = template_by_role(current_user, 'custom/cms/player_message.html',
                                                   'custom/cms/gm_message.html',
                                                   'custom/cms/admin_message.html')
    return render_template(template_name,
                           user=current_user,
                           usermsg='class=active')


@bp.route('user/message/list', methods=['GET', ])
@login_required
def user_message_list():
    if request.method == 'GET':
        message_list = current_user.messages.all()
        return render_template('custom/cms/profile_title_message_list.html',
                               mlist=enumerate(message_list))


@bp.route('message/details/<int:index>', methods=['GET', ])
@login_required
def get_message_content(index):

    index -= 1
    all_message = (msg.message for msg in current_user.messages)
    message_list = list(all_message)
    err_handle = lambda : {'title':   u'索引无效',
                           'content': u'不是有效的索引，请返回重新查询',
                           'created': datetime.datetime.now()
                           }
    if index < 0 or index >= len(message_list):
        message = err_handle()
    else:
        try:
            message = message_list[index]
        except IndexError:
            message = err_handle()
        else:
            associate = message.users_assocs[0]
            associate.is_read = True
            db.session.add(associate)
            db.session.commit()

    template_name = 'custom/cms/profile_title_message_content.html'
    return render_template(template_name, message=message)


@bp.route('upgrade-table', methods=['GET', ])
@login_required
def upgrade_online():

    user = current_user
    template_name = template_by_role(user, 'custom/cms/player_upgrade_table.html',
                                           'custom/cms/gm_upgrade_table.html',
                                           'custom/cms/admin_upgrade_table.html')

    online = round(user.update_time / 3600.0, 1)   # 取一位小数,计算在线时间
    num = get_permission_num()                     # 最高三个权限不能直升
    if online > time_by_level(num):
        online = time_by_level(num)
    x_axis = range(1, num + 1)
    gen = (time_by_level(level) for level in x_axis)
    y_axis = list(gen)

    # 当前等级下的在线时间
    cur_level = level_by_permission_value(user.permission.value)
    online_axis = y_axis[:cur_level]
    if cur_level <= num:                          # 过滤最高的三个权限的升级时间
        online_axis[-1] = online

    color = ['rgba(0,0,0,',
             'rgba(255,99,132,',
             'rgba(54,162,235,',
             'rgba(255,206,86,',
             'rgba(75,192,192,',
             'rgba(153,102,255,',
             'rgba(255,159,64,']

    def f_color(hx, number):
        if len(hx) >= number:
            return hx[0:number]
        elif len(hx) < number:
            n = int(math.ceil(float(number)/len(hx)))
            return (hx * n)[0:number]

    param = {'user': user, 'profile': 'class=active'}
    param['chartLabel1'] = u'升级所需时间'
    param['chartLabel2'] = u'当前在线时间'
    param['x_axis'] = x_axis
    param['y_axis'] = y_axis
    param['online'] = online_axis              # [online]*num
    param['color'] = ['rgba(0,0,0,']*num       # f_color(color, num)

    return render_template(template_name, **param)


@bp.route('permission-table', methods=['GET', ])
@login_required
def permission_table():

    user = current_user
    template_name = template_by_role(user, 'custom/cms/player_permission_table.html',
                                           'custom/cms/gm_permission_table.html',
                                           'custom/cms/admin_permission_table.html',)

    param = {'user': user, 'profile': 'class=active'}
    # ps = get_all_permission(need_value=False)
    rs = find_all_roles(need_label=True)
    # 一个权限有多个角色
    roles = []
    titles = [u'值']

    [(titles.append(role[1]), roles.append(role[0])) for role in rs]
    param['titles'] = titles

    rows = []
    for level in xrange(1, get_permission_num()+1):
        title_row = []
        current_row = [permission_value_by_level(level)]
        level_p = get_permission_by_level(level)
        for role in roles:
            title_p = get_permission_by_role(role)
            if level_p and title_p and level_p >= title_p:
                title_row.append('glyphicon glyphicon-ok')
            else:
                title_row.append('glyphicon glyphicon-remove')
        current_row.append(tuple(title_row))
        rows.append(tuple(current_row))
    param['rows'] = rows
    param['cur_per'] = user.permission.value

    return render_template(template_name, **param)


# @bp.route('profile/update-account', methods=['GET', ])
# @login_required
# def profile_update_account():
#     user = current_user
#     update_id = request.args.get('id')
#     async_task = tasks.tasksDict.pop(update_id, None)
#     # async_task = None
#     if not async_task:
#         async_task = tasks.update_account_by_name.delay(user.username)
#     try:
#         result = async_task.get(timeout=5)
#         # result = async_task
#     except TimeoutError, e:
#         rst = {'status': 'Err', 'msg': u'操作超时'}, 200
#     else:
#         if result[0]:
#             races = []
#             prompts = []
#             characters = Characters.query.filter_by(user_id=user.id).all()
#             if characters:
#                 cnt = len(characters)
#                 prompts.append([random_prompt(AlivePrompt, ch.alive) for ch in characters])
#                 for m in [LevelPrompt, RacePrompt, JobPrompt, GenderPrompt, MoneyPrompt]:
#                     prompts.append([random_prompt(m) for i in range(cnt)])
#
#                 for ch in characters:
#                     if ch.side == 'LM':
#                         _races = app.config['WOW_RACE_ALLIANCE']
#                     else:
#                         _races = app.config['WOW_RACE_HORDE']
#
#                     races.append([race for race in _races if race != ch.race])
#
#             rst = {'status': 'Ok', 'characters': [ch.to_json() for ch in characters], 'races': races, 'prompts': prompts,
#                    'msg': result[1] if len(characters) else u'还没有创建角色,快去游戏创建再来刷新'}, 200
#         else:
#             rst = {'status': 'Err', 'msg': result[1]}, 200
#
#     json_data = jsonify(**rst[0])
#     return json_data, rst[1]
#
#
# @bp.route('profile', methods=['GET', ])
# @bp.route('profile/characters', methods=['GET', ])
# @login_required
# def profile_page():
#     user = current_user
#     if not user.update_time:  # or (datetime.datetime.now() - user.update_time) > datetime.timedelta(1):
#         result = tasks.update_account_by_name.delay(user.username)
#         template_name = template_by_role(user, 'custom/cms/player_characters_update.html',
#                                                'custom/cms/gm_characters_update.html',
#                                                'custom/cms/admin_characters_update.html')
#         update_id = gen_rnd_string(18)
#         tasks.tasksDict[update_id] = result
#
#         return render_template(template_name,
#                                user=user,
#                                character='class=active',
#                                update_id=update_id), 202
#     else:
#         template_name = template_by_role(user, 'custom/cms/player_characters.html',
#                                                'custom/cms/gm_characters.html',
#                                                'custom/cms/admin_characters.html')
#         characters = Characters.query.filter_by(user_id=user.id).all()
#         races = []
#         prompts = []
#         if characters:
#             cnt = len(characters)
#             prompts.append([random_prompt(AlivePrompt, ch.alive) for ch in characters])
#             for m in [LevelPrompt, RacePrompt, JobPrompt, GenderPrompt, MoneyPrompt]:
#                 prompts.append([random_prompt(m) for i in range(cnt)])
#
#             for ch in characters:
#                 if ch.side == 'LM':
#                     _races = app.config['WOW_RACE_ALLIANCE']
#                 else:
#                     _races = app.config['WOW_RACE_HORDE']
#
#                 races.append(enumerate([race for race in _races if race != ch.race]))
#
#     return render_template(template_name,
#                            user=user,
#                            character='class=active',
#                            characters=enumerate(characters),
#                            races=races,
#                            prompts=prompts)
#
#
# @bp.route('refresh-character', methods=['GET', ])
# @login_required
# def refresh_character():
#     character_name = request.args.get('id', '')
#     if character_name:
#         one = Characters.query.filter(Characters.name == character_name, Characters.user_id == current_user.id).first()
#         if one:
#             queryData = tasks.query_characters(one.guid)
#             if queryData[0]:
#                 new_one = update_wowaccount_characters(current_user, json.loads(queryData[1]))
#                 if new_one:
#                     rst = {'alive': random_prompt(AlivePrompt, new_one.alive),
#                            'level': new_one.level,
#                            'race': new_one.race,
#                            'job': new_one.job,
#                            'gender': new_one.gender,
#                            'money': new_one.money,
#                            'last_login': new_one.last_login.strftime("%Y-%m-%d %H:%M:%S"),
#                            'played_time': new_one.played_time,
#                            'status': 'Ok'}, 200
#                 else:
#                     rst = {'status': 'Err', 'msg': u'角色不存在'}, 200
#             else:
#                 rst = {'status': 'Err', 'msg': queryData[1]}, 200
#         else:
#             rst = {'status': 'Err', 'msg': u'当前账户下不存在此角色'}, 200
#     else:
#         rst = {'status': 'Err', 'msg': u'参数错误'}, 200
#     return jsonify(**rst[0]), rst[1]
#
#
# @bp.route('profile/promote-character', methods=['POST'])
# @login_required
# def promote_character():
#     """
#     pk :  1 :等级提升
#           2 :种族切换
#           3 :职业更改,(更改没意义)
#           4 :变性
#           5 :送钱, 10000:1
#     value : 升级的等级\变成的种族\更改的职业\变的性\要的钱
#     name  : 操作对象
#     """
#
#     if request.method == 'POST':
#         form = PromoteForm(**request.form)
#         if form.validate():
#             is_exist = Characters.query.filter(Characters.name == form.name, Characters.user_id == current_user.id).first()
#             if is_exist:
#                 try:
#                     rst = 'Ok', u'提交成功'
#                     if form.pk == 1:
#                         if get_permission_by_role('UPLEVEL', False) in current_user.roles.all():
#                             tasks.level_character(form.name, form.value)
#                         else:
#                             rst = 'Err', u'权限不够'
#                     elif form.pk == 2:
#                         rls = current_user.roles.all()
#                         if get_permission_by_role('CHRACE', False) in current_user.roles.all():
#                             tasks.change_race(form.name)
#                         else:
#                             rst = 'Err', u'权限不够'
#                     elif form.pk == 4:
#                         if get_permission_by_role('CUSTOMIZE', False) in current_user.roles.all():
#                             if is_exist.gender.upper() == u'Male'.upper() and form.value == 2 \
#                                     or is_exist.gender.upper() == u'female'.upper() and form.value == 1:
#                                 tasks.change_gender(form.name)
#                         else:
#                             rst = 'Err', u'权限不够'
#                     elif form.pk == 5:
#                         if get_permission_by_role('GETMONEY', False) in current_user.roles.all():
#                             money = random.randint(1, 9000) if form.value == 1 else 4000 if form.value == 2 else 1
#                             tasks.send_money(form.name, 'A Gift', 'Enjoy Game', 10000*money)
#                         else:
#                             rst = 'Err', u'权限不够'
#                     else:
#                         rst = 'Err', u'参数错误'
#                 except Exception, e:
#                     result = {'status': 'Err', 'msg': u'与服务器通信异常'}
#                 else:
#                     result = {'status': rst[0], 'msg': rst[1]}
#             else:
#                 result = {'status': 'Err', 'msg': u'当前账户下不存在此角色'}
#         else:
#             result = {'status': 'Err', 'msg': u'请求参数错误'}
#     else:
#         result = {'status': 'Err', 'msg': u'请求类型错误'}
#
#     return jsonify(result)

# Register blueprint
add_blueprint(bp)
