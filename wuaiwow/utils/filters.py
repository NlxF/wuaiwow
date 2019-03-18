# coding:utf-8
import time
import datetime
from wuaiwow import app


def readable_elapse(past):
    now = datetime.datetime.fromtimestamp(time.time())
    try:
        elapse = now - past
    except TypeError:
        return u'时间未知'

    return str(elapse.seconds // 3600) + u" 小时前" if elapse.days == 0 else u"昨天" if elapse.days == 1 else u"前天" if elapse.days == 2 else str(
        elapse.days) + u" 天前" if isinstance(elapse, datetime.datetime) else u'时间未知'


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    _format = '%Y-%m-%d' if not fmt else fmt
    if isinstance(date, datetime.datetime):
        return date.strftime(_format)
    else:
        return 'Need datetime type provide %s' % type(date)


@app.template_filter('timespan')
def _jinja2_filter_timespan(date):
    return readable_elapse(date)


@app.template_filter('struct')
def _jinja2_filter_struct(msg):
    if msg.has_read:
        return "openenvelope"
    else:
        return "closenvelope"


@app.template_filter('isread')
def _jinja2_filter_isread(msg):
    if msg.has_read:
        return "glyphicon glyphicon-eye-open"
    else:
        return "glyphicon glyphicon-eye-close"


@app.template_filter('summary')
def _jinja2_filter_summary(content):
    content_len = len(content)
    summary_len = 20 if content_len < 20 else content_len

    return content[:summary_len]


@app.template_filter('hasRole')
def _jinja2_filter_summary(permission, role_obj):
    return role_obj.role in (prole.role.role for prole in permission.roles)