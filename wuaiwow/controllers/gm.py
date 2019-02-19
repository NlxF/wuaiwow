# coding:utf-8
from flask import (render_template, Blueprint, request, url_for,
                   make_response, jsonify)
from flask_user import current_user, login_required
from wuaiwow.utils import add_blueprint, save_file_upload
from wuaiwow.utils.accountHelper import permission_required
from wuaiwow.utils.templateHelper import template_by_role
from wuaiwow.utils.modelHelper import (find_or_create_news,
                                       get_permission_by_role,
                                       find_or_create_permission,
                                       get_permission_by_value, get_user_by_name,
                                       get_less_permission, get_less_permission_user,
                                       create_guild_info, get_latest_guild_info, get_all_news,
                                       get_role_by_name)
from wuaiwow import app, db, csrf


bp = Blueprint('GM', __name__, url_prefix='/gm')


@bp.route('/add-news', methods=['GET', 'POST'])
@login_required
@permission_required(get_permission_by_role('GM'))
def add_news():
    default_url = url_for('static', filename='images/default_title.jpg')

    if request.method == 'POST':
        if request.form['news-title']:
            one_news, exist = find_or_create_news(request.form['news-title'])
            if request.files and request.files['news-photo']:
                f = request.files['news-photo']
                try:
                    file_name = save_file_upload(f, app.config['ALLOWED_EXTENSIONS'], app.static_folder)
                    photo_url = url_for('static', filename=file_name)
                except Exception, e:
                    photo_url = default_url
            else:
                photo_url = default_url

            if not one_news.image_url or photo_url != default_url:
                one_news.image_url = photo_url
            one_news.content = request.form['news-content']
            db.session.add(one_news)
            db.session.commit()

            titles = [one.title for one in get_all_news()]
            titles.insert(0, u"选择新闻编辑或新建新闻" if titles else u"还未添加新闻")
            result = {'status': 'Ok', 'msg': u'修改成功' if exist else u'添加成功', 'photo_url': one_news.image_url,
                      'titles': titles, 'selected': titles.index(one_news.title)}
        else:
            result = {'status': 'Err', 'msg': u'标题不能为空', 'photo_url': default_url}
        return jsonify(result)
    else:
        photo_url = default_url

    template_name = template_by_role(current_user, 'custom/cms/gm_add_news.html',
                                                   'custom/cms/admin_add_news.html')

    titles = [one.title for one in get_all_news()]
    titles.insert(0, u"选择新闻编辑或新建新闻" if titles else u"还未添加新闻")

    return render_template(template_name, user=current_user,
                           addnews='class=active',
                           titles=enumerate(titles),
                           photo=photo_url)


@bp.route('/get-a-news', methods=['GET'])
@login_required
@permission_required(get_permission_by_role('GM'))
def get_a_news():
    news_id = request.args.get('id', '')
    news = get_all_news()
    selected = news[int(news_id)-1] if len(news) >= int(news_id) else None
    if selected:
        result = {'status': 'Ok', 'msg': u'OK', 'news_title': selected.title,
                  'news_content': selected.content, 'news_photo': selected.image_url}
    else:
        result = {'status': 'Err', 'msg': u'不存在此新闻'}
    return jsonify(result)


@bp.route('/add-tutorial', methods=['GET', 'POST'])
@login_required
@permission_required(get_permission_by_role('GM'))
def add_tutorial():
    if request.method == 'POST':
        guild_info = request.form['guildinfotext']
        # guild = GuildInfo(info=guild_info)
        guild = create_guild_info(info=guild_info)
        try:
            db.session.add(guild)
            db.session.commit()
        except Exception, e:
            result_info = {'retCode': 0, 'retMsg': u'更新失败,再试下'}
        else:
            result_info = {'retCode': 1, 'retMsg': u'更新成功'}
    else:
        result_info = {}
        # guild = GuildInfo.query.order_by(GuildInfo.date.desc()).first()
        guild = get_latest_guild_info()
        guild_info = guild.info if guild else ' '

    template_name = template_by_role(current_user, 'custom/cms/gm_add_tutorial.html',
                                                   'custom/cms/admin_add_tutorial.html')
    return render_template(template_name,
                           user=current_user,
                           addtutorial='class=active',
                           guild_info=guild_info,
                           result=result_info)


@csrf.exempt
@bp.route('upload/images', methods=['POST', 'OPTIONS'])
@login_required
@permission_required(get_permission_by_role('GM'))
def upload_images():
    """CKEditor images upload"""
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")

    if request.method == 'POST' and 'upload' in request.files:
        file_obj = request.files['upload']
        try:
            file_name = save_file_upload(file_obj, app.config['ALLOWED_EXTENSIONS'], app.static_folder)
            url = url_for('static', filename=file_name)
        except Exception, e:
            error = e.message
    else:
        error = 'post error'

    res = """<script type="text/javascript">
              window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
            </script>""" % (callback, url, error)

    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response


@bp.route('/change-user-role/', methods=['GET', ])
@login_required
@permission_required(get_permission_by_role('GM'))
def change_user_role():

    template_name = template_by_role(current_user, 'custom/cms/gm_add_role.html',
                                                   'custom/cms/admin_add_role.html')
    return render_template(template_name,
                           user=current_user,
                           addrole='class=active')


@bp.route('/user-role-list/', methods=['GET', 'POST'])
@login_required
@permission_required(get_permission_by_role('GM'))
def role_list():
    if request.method == 'POST':
        form = request.form
        try:
            pk = int(form['pk'])
            value = int(form['value'])
        except (ValueError, KeyError):
            pk = value = -1
        if pk == 101 and value < current_user.permission.value:
            new_perm = get_permission_by_value(value=value)
            if new_perm is not None:
                user = get_user_by_name(name=form['name'])
                if user:
                    if user.permission != new_perm:
                        user.change_user_permission(new_perm)
                        db.session.commit()

                        # 同步game server端的account-permission表
                        from wuaiwow import tasks
                        tasks.update_account_permission.delay([(user.username, new_perm.value)])
                    result = {'status': 'Ok', 'msg': u'修改成功', 'newValue': value}
                else:
                    result = {'status': 'Err', 'msg': u'用户不存在'}
            else:
                result = {'status': 'Err', 'msg': u'权限不存在'}
        else:
            result = {'status': 'Err', 'msg': u'参数错误'}
    else:
        user_permission = current_user.permission     # 当前用户的权限, 修改的权限只能低于自己
        ps = [p.value for p in get_less_permission(user_permission.value)]
        # roles = list()
        # roles.extend([r.role for p in ps for r in p.roles])      # 当前用户权限所拥有的角色
        users = get_less_permission_user(user_permission.value)  # 过滤比当前用户权限高的

        # get_last_role = lambda rs: rs[-1].role if len(rs) else 'CHRACE'
        rows = [{"id": value + 1,
                 "name": u.username,
                 "perm": u.permission.value,
                 "perms": ps} for value, u in enumerate(users)]

        result = {'status': 'Ok', 'rows': rows}

    return jsonify(result)


# Register blueprint
add_blueprint(bp)
