# --* coding:utf-8 *--
from flask import render_template, Blueprint, request, jsonify, url_for
from flask_user import current_user, login_required
from wuaiwow import db, app, tasks
from wuaiwow.utils import add_blueprint, save_file_upload
from wuaiwow.utils.templateHelper import all_prompt
from wuaiwow.utils.accountHelper import permission_required
from wuaiwow.utils.modelHelper import (find_or_create_sidebar,
                                       get_permission_by_role, get_permission_by_value,
                                       find_or_create_permission,
                                       find_all_roles, get_role_by_name,
                                       get_all_permission, get_permission_num,
                                       permission_value_by_level, add_role_to_permission,
                                       create_role)
from wuaiwow.models import (Donate, LevelPrompt, AlivePrompt, RacePrompt, Agreement,
                            JobPrompt, GenderPrompt, MoneyPrompt, Sidebar, Permission)

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/add-donate', methods=['GET', 'POST'])
@login_required
@permission_required(get_permission_by_role('UPGRADE'))
def add_donate():
    result_info = ''
    if request.method == 'POST':
        donate_info = request.form['donateinfotext']
        donate = Donate(info=donate_info)
        try:
            db.session.add(donate)
            db.session.commit()
        except Exception, e:
            result_info = u'更新失败,再试下'
        else:
            result_info = u'更新成功'
    else:
        donate = Donate.query.order_by(Donate.date.desc()).first()
        donate_info = donate.info if donate else " "

    return render_template('custom/cms/admin_add_donate.html',
                           user=current_user,
                           adddonate='class=active',
                           donate_info=donate_info,
                           result=result_info)


@bp.route('/add-userAgreement', methods=['GET', 'POST'])
@login_required
@permission_required(get_permission_by_role('UPGRADE'))
def add_user_agreement():
    result_info = ''
    if request.method == 'POST':
        content = request.form['agreement-content']
        donate = Agreement(content=content)
        try:
            db.session.add(donate)
            db.session.commit()
        except Exception, e:
            result_info = u'更新失败,再试下'
        else:
            result_info = u'更新成功'
    else:
        agreement = Agreement.query.order_by(Agreement.update.desc()).limit(5).first()
        content = agreement.content if agreement else " "

    return render_template('custom/cms/admin_add_userAgreement.html',
                           user=current_user,
                           adduseragreement='class=active',
                           content=content,
                           result=result_info)


@bp.route('/add-prompt', methods=[])
@login_required
@permission_required(get_permission_by_role('UPGRADE'))
def add_prompt():
    if request.method == 'POST':
        form = request.get_json()
        try:
            for m in [AlivePrompt, LevelPrompt, RacePrompt, JobPrompt, GenderPrompt, MoneyPrompt]:
                if form['id'] and form['id'] == m.class_id():
                    if form['id'] == 'alive':
                        inst = m(prompt=form['value'], alive=True if form['type'] == '1' else False)
                    else:
                        inst = m(prompt=form['value'])
                    db.session.add(inst)
                    db.session.commit()
                    result = {'status': 'Ok', 'msg': u'添加成功', 'value': form['value']}
                    break
            else:
                result = {'status': 'Err', 'msg': u'添加提示语类型错误'}
        except Exception, e:
                result = {'status': 'Err', 'msg': u'未知错误'}
        return jsonify(result)
    else:
        rst = []
        for m in [AlivePrompt, LevelPrompt, RacePrompt, JobPrompt, GenderPrompt, MoneyPrompt]:
            prompt = all_prompt(m)
            prompt_dict = {'id': m.class_id(), 'title': m.title(), 'prompt': enumerate(prompt)}
            rst.append(prompt_dict)
        return render_template('custom/cms/admin_add_prompt.html',
                               user=current_user,
                               prompts=rst,
                               addprompt='class=active')


@bp.route('/del-prompt', methods=[])
@login_required
@permission_required(get_permission_by_role('UPGRADE'))
def del_prompt():
    if request.method == 'POST':
        form = request.get_json()
        try:
            for m in [AlivePrompt, LevelPrompt, RacePrompt, JobPrompt, GenderPrompt, MoneyPrompt]:
                if form['id'] and form['id'] == m.class_id():
                    inst = m.query.filter_by(prompt=form['value']).first()
                    if inst:
                        db.session.delete(inst)
                        db.session.commit()
                        result = {'status': 'Ok', 'msg': u'删除成功'}
                    else:
                        result = {'status': 'Err', 'msg': u'提示语不存在'}
                    break
            else:
                result = {'status': 'Err', 'msg': u'要删除的提示语类型错误'}
        except Exception,e:
            result = {'status': 'Err', 'msg': u'未知错误'}
    else:
        result = {'status': 'Err', 'msg': u'请求类型错误'}

    return jsonify(result)


@bp.route('/add-sidebar', methods=['GET', 'POST'])
@login_required
@permission_required(get_permission_by_role('UPGRADE'))
def add_sidebar():
    default_url = url_for('static', filename='images/default_title.jpg')
    sidebars = [sd.name for sd in Sidebar.query.order_by(Sidebar.created.asc()).all()]
    if request.method == 'POST':
        if request.form['sidebar-name']:
            sd = find_or_create_sidebar(request.form['sidebar-name'])
            if request.files and request.files['sidebar-photo']:
                f = request.files['sidebar-photo']
                try:
                    file_name = save_file_upload(f, app.config['ALLOWED_EXTENSIONS'], app.static_folder)
                    photo_url = url_for('static', filename=file_name)
                except Exception, e:
                    photo_url = default_url
            else:
                photo_url = default_url

            if not sd.image_url or photo_url != default_url:
                sd.image_url = photo_url
            sd.content = request.form['sidebar-content']
            db.session.add(sd)
            db.session.commit()

            sidebars.insert(0, sd.name)
            sidebars.insert(0, u"选择侧边栏编辑或新建侧边栏" if sidebars else u"还未添加侧边栏")
            result = {'status': 'Ok', 'msg': u'添加成功', 'photo_url': sd.image_url, 'titles': sidebars}
        else:
            result = {'status': 'Err', 'msg': u'名称不能为空', 'photo_url': default_url}
        return jsonify(result)
    else:
        photo_url = default_url

    sidebars.insert(0, u"选择侧边栏编辑或新建侧边栏" if sidebars else u"还未添加侧边栏")

    return render_template('custom/cms/admin_add_sidebar.html'
                           , user=current_user,
                           addsidebar='class=active',
                           sidebars=enumerate(sidebars),
                           photo=photo_url)


@bp.route('/get-a-sidebar', methods=['GET'])
@login_required
@permission_required(get_permission_by_role('UPGRADE'))
def get_a_sidebar():
    sd_id = request.args.get('id', '')
    sds = Sidebar.query.order_by(Sidebar.created.desc()).all()
    selected = sds[int(sd_id)-1] if len(sds) >= int(sd_id) else None
    if selected:
        result = {'status': 'Ok', 'msg': u'OK', 'sidebar_name': selected.name,
                  'sidebar_content': selected.content, 'sidebar_photo': selected.image_url}
    else:
        result = {'status': 'Err', 'msg': u'此侧边栏不存在'}
    return jsonify(result)


@bp.route('/change-role-permission/', methods=['GET', 'POST'])
@login_required
@permission_required(get_permission_by_role('UPGRADE'))
def change_role_permission():
    if request.method == 'POST':
        role_permission = request.form.get('newRolePerm', "")
        if not role_permission:
            result = {'status': 'Err', 'msg': u'参数错误'}
        else:
            command_list = []
            role_perm = [a.split('=') for a in role_permission.split('&')]
            for r, v in role_perm:
                created, ps = find_or_create_permission(value=v)
                role = get_role_by_name(role=r)
                if ps and role not in ps.roles:
                    added, _ = add_role_to_permission(ps=ps, role=role)                   # 更新权限拥有的role
                    if added:
                        command_list.append((ps.value, role.role, role.label))            # 保存更改成功的记录
            else:
                db.session.commit()
                result = {'status': 'Ok', 'msg': u'修改成功'}

            if len(command_list) > 0:
                # 更新game server端的对应表
                tasks.update_permission_table(command_list)

        return jsonify(result)
    else:
        role_value = find_all_roles(need_label=True)

        values = get_all_permission(need_value=True)

        return render_template('custom/cms/admin_permission.html',
                               user=current_user,
                               addpermission='class=active',
                               roles=role_value,
                               selected=values)


@bp.route('/add-permission/', methods=['GET', ])
@login_required
@permission_required(get_permission_by_role('UPGRADE'))
def add_permission():
    max_level = get_permission_num()
    next_permission_value = permission_value_by_level(max_level + 1)
    if next_permission_value > 98:
        result = {'status': 'Err', 'msg': u'添加失败,已没有空余位置新增权限'}
    else:
        created, ps = find_or_create_permission(value=next_permission_value, need_created=True)
        if created:
            db.session.commit()

        result = {'status': 'Ok', 'msg': u'添加成功'}

    return jsonify(result)


@bp.route('/add-role/', methods=['POST', ])
@login_required
@permission_required(get_permission_by_role('UPGRADE'))
def add_role():
    new_role = request.form.get('newRole', "")
    new_value = request.form.get('newValue', -1)
    new_label = request.form.get('newLabel', "")
    try:
        new_value = int(new_value)
    except ValueError:
        return jsonify({'status': 'Err', 'msg': u'参数错误'})

    if new_value < 0 or new_value > 100:
        result = {'status': 'Err', 'msg': u'参数错误'}
    else:
        role_obj = get_role_by_name(role=new_role)
        if not role_obj:
            role_obj = create_role(role=new_role, label=new_label)
        ps = get_permission_by_value(value=new_value)
        success, rst = add_role_to_permission(ps=ps, role=role_obj)
        if success:
            db.session.commit()
            result = {'status': 'Ok', 'msg': u'添加成功'}

            # 更新game server端的permission表
            tasks.update_permission_table([(ps.value, role_obj.role, role_obj.label)])
        else:
            result = {'status': 'Err', 'msg': rst}

    return jsonify(result)


# Register blueprint
add_blueprint(bp)
