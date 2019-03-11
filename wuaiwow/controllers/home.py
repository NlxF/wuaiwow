# coding:utf-8
import os
import json
import time
import urllib2
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session
from flask import jsonify
# from flask_wtf.csrf import CsrfProtect
from flask_user import current_user, login_required
from flask_user.signals import user_logged_in, user_logged_out
from wuaiwow import app, db, onlineHelper
from wuaiwow.utils import add_blueprint, filters
from wuaiwow.models import UserIp, News
from wuaiwow.utils.modelHelper import (get_news_by_index_num, get_all_sidebar, get_latest_guild_info,
                                       get_latest_donate_info, get_latest_agreement_info)

# csrf = CsrfProtect()
bp = Blueprint('wuaiwow', __name__, template_folder='templates', static_folder='static', url_prefix='/')


# The Home page
@bp.route('', methods=['GET', ])
def home_page():
    start_idx, length = 0, session.pop("scount", 5)
    first_10_news = get_news_by_index_num(index=start_idx, number=length)
    session.setdefault("scount", len(first_10_news))
    # session.permanent = False
    all_sidebar = get_all_sidebar()
    return render_template('custom/home.html',
                           user=current_user,
                           all_news=first_10_news,
                           all_sidebar=all_sidebar*2)


@bp.route('blog-load-more/<int:index>/<int:count>')
def more_blog(index, count):
    rst = []
    if index >= 0 and count > 0:
        more_news = get_news_by_index_num(index, count)
        session.setdefault("scount", len(more_news)+index)
        readable_date = lambda past_days: u"今天" if past_days == 0 else u"昨天" if past_days == 1 else u"前天" if past_days == 2 else str(past_days)+u" 天前"
        now = datetime.datetime.fromtimestamp(time.time())
        [rst.append({'id': one_news.id,
                     'title': one_news.title,
                     'content': one_news.content,
                     'image': one_news.image_url,
                     'date': one_news.update,
                     'readable_date': readable_date((now-one_news.update).days) if isinstance(one_news.update, datetime.datetime) else u'时间未知' })
         for one_news in more_news]

    return jsonify(result=rst)


@bp.route('tutorial', methods=['GET', ])
def tutorial():
    guild = get_latest_guild_info()
    if not guild:
        tutorial_info = u'还未更新教程'
    else:
        tutorial_info = guild.info

    return render_template('custom/tutorial.html', user=current_user, tutorial=tutorial_info)


@bp.route('donate', methods=['GET', ])
def donate():
    _donate = get_latest_donate_info()
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
    agreement = get_latest_agreement_info()
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
    # noinspection PyBroadException
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
