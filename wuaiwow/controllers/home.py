# coding:utf-8
import os
import json
import time
import urllib2
from multiprocessing import current_process
from flask import Blueprint, render_template, request, redirect, url_for, render_template_string
from flask import jsonify
# from flask_wtf.csrf import CsrfProtect
from flask_user import current_user, login_required
from flask_user.signals import user_logged_in, user_logged_out
from wuaiwow import app, db, onlineHelper, share_data_manager
from wuaiwow.utils import add_blueprint, filters
from wuaiwow.models import GuildInfo, Donate, UserIp, News, Sidebar, Agreement

from threading import Thread, current_thread

# csrf = CsrfProtect()
bp = Blueprint('wuaiwow', __name__, template_folder='templates', static_folder='static', url_prefix='/')

# test data share
@bp.route('test/fork', methods=['GET', ])
def fork_test():
    print(os.getpid(), current_thread())
    cur_process = current_process()
    if 'test' not in share_data_manager:
        share_data_manager['test'] = 0;
    share_data_manager['test'] = share_data_manager['test'] + 1;
    msg = "current_process:{}-{} with share data manager:{}-{}".format(cur_process, os.getpid(), id(share_data_manager), share_data_manager['test'])
    print(msg)
    time.sleep(5.)
    return render_template_string(msg)

# The Home page
@bp.route('')
def home_page():
    user = current_user
    all_news = News.query.order_by(News.update.desc()).limit(10).all()
    all_sidebar = Sidebar.query.order_by(Sidebar.id.asc()).all()
    return render_template('custom/home.html',
                           user=user,
                           all_news=all_news,
                           all_sidebar=all_sidebar*2)


@bp.route('blog-load-more/<int:index>/<int:count>')
def more_blog(index, count):
    l = []
    url = '/wow/zh/blog/17406774/%E9%AD%94%E5%85%BD%E4%B8%96%E7%95%8C%E5%8A%A8%E6%80%81-2015%E5%B9%B410%E6%9C%88-2015%E5%B9%B410%E6%9C%881%E6%97%A5'
    title = '魔兽世界动态——2015年10月'
    content = '10月节庆，欢乐多多！美酒节的饕餮盛宴过后迎来了万圣节的趣味游戏。赶快来计划一下怎么度过你的10月，因为稍不留神，幸福的时光就会匆匆离去！'
    image = '//cms-origin-cn.battle.net/cms/blog_thumbnail/dt/DTBMVIX5O6T41438245811789.jpg'
    date = '1 day age'
    dic = {'url': url, 'title': title, 'content': content, 'image': image, 'date': date}
    l.append(dic)
    l.append(dic)

    return jsonify(result=l)


@bp.route('tutorial', methods=['GET', ])
def tutorial():
    guild = GuildInfo.query.order_by(GuildInfo.date.desc()).first()
    if not guild:
        tutorial_info = u'还未更新教程'
    else:
        tutorial_info = guild.info

    return render_template('custom/tutorial.html', user=current_user, tutorial=tutorial_info)


@bp.route('donate', methods=['GET', ])
def donate():
    _donate = Donate.query.order_by(Donate.date.desc()).first()
    if not _donate:
        donate_info = u'还未更新捐赠信息'
    else:
        donate_info = _donate.info

    return render_template('custom/donate.html', user=current_user, donate=donate_info)


@bp.route('wuaiwow/news/<int:index>/<string:title>')
def news(index, title):
    hash_id = hash(title)
    news = News.query.filter(News.id == index, News.title == title).first()
    if news:
        pass
    else:
        pass
    return render_template('custom/detail_news.html')


@bp.route('wuaiwow/sidebar/<int:index>/<string:name>')
def sidebar(index, name):

    return render_template('custom/sidebar_download.html')


@bp.route('user-agreement/')
def user_agreement():
    agreement = Agreement.query.order_by(Agreement.update.desc()).first()
    if not agreement:
        content = u'还未更新用户协议'
    else:
        content = agreement.content

    return render_template('custom/agreement.html', user=current_user, content=content)


@user_logged_in.connect_via(app)
def _track_login(sender, user, **extra):
    ips = UserIp.query.filter_by(user=user).order_by(UserIp.login_time).all()
    if len(ips) == 10:
        ip = ips[0]
    else:
        ip = UserIp()
    ip.user = user
    ip.address = request.remote_addr
    try:
        url = app.config['URL_QUERY'] + ip.address
        resp = urllib2.urlopen(url, timeout=5)
        address_json = resp.read()
        address_dict = json.loads(address_json)
        if address_dict['status'] == 0:
            content = address_dict.get('content', None)
            address_detail = content.get('address_detail', None)
            if address_detail:
                ip.province = address_detail['province'] if len(address_detail['province']) else u'未知'
                ip.city = address_detail['city'] if len(address_detail['city']) else u'未知'
                ip.district = address_detail['district'] if len(address_detail['district']) else u'未知'
                ip.street = address_detail['street'] if len(address_detail['street']) else u'未知'
    except Exception as e:
        # pass
        ip.province = ip.city = ip.district = ip.street = u'未知'

    user.ips.append(ip)

    db.session.add(user)
    db.session.add(ip)
    db.session.commit()


@user_logged_out.connect_via(app)
def _track_logout(sender, user, **extra):
    if not current_user.is_anonymous:
        onlineHelper.make_user_offline(current_user.username)   # 退出账号时设为离线状态


# Register blueprint
add_blueprint(bp)
