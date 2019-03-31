# coding:utf-8
import os
# import math
import string
import random
import datetime
from PIL import Image
from flask_mail import Mail
from flask_cache import Cache
from flask_babel import Babel
from flask_debugtoolbar import DebugToolbarExtension
from flask_user import UserManager, SQLAlchemyAdapter
from werkzeug.utils import secure_filename
from plugHelper import add_blueprint


def configure_extensions(app, db):
    """configure app extensions"""

    # Setup Flask-Mail
    mail = Mail(app)

    # Setup Cache
    app.cache = Cache(app)

    # i18n
    babel = Babel(app)

    # Setup DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)

    # Define bootstrap_is_hidden_field for flask-bootstrap's bootstrap_wtf.html
    # from wtforms.fields import HiddenField
    #
    # def is_hidden_field_filter(field):
    #     return isinstance(field, HiddenField)
    #
    # app.jinja_env.globals['bootstrap_is_hidden_field'] = is_hidden_field_filter

    # Setup Flask-User to handle user account related forms
    from wuaiwow.models.users import User, UserInvitation
    from wuaiwow.forms import MyRegisterForm, MyLoginForm, MyChangePasswordForm

    # Setup the SQLAlchemy DB Adapter
    db_adapter = SQLAlchemyAdapter(db, User, UserEmailClass=None, UserInvitationClass=UserInvitation)
    # using a custom register form with UserProfile fields
    from wuaiwow.controllers.users import register, change_password, reset_password   # user_profile
    from wuaiwow.controllers.player import user_account
    user_manager = UserManager(db_adapter, app,
                               register_form=MyRegisterForm,
                               register_view_function=register,
                               login_form=MyLoginForm,
                               change_password_form=MyChangePasswordForm,
                               change_password_view_function=change_password,
                               reset_password_view_function=reset_password,
                               user_profile_view_function=user_account)

    return app


def init_email_error_handler(app, level):
    """
    Initialize a logger to send emails on error-level messages.
    Unhandled exceptions will now send an email message to app.config.ADMINS.
    """
    if app.debug:
        return  # Do not send error emails while developing

    # Retrieve email settings from app.config
    host = app.config['MAIL_SERVER']
    port = app.config['MAIL_PORT']
    from_addr = app.config['MAIL_DEFAULT_SENDER']
    username = app.config['MAIL_USERNAME']
    password = app.config['MAIL_PASSWORD']
    secure = () if app.config.get('MAIL_USE_TLS') else None

    # Retrieve app settings from app.config
    to_addr_list = app.config['ADMINS']
    subject = app.config.get('APP_SYSTEM_ERROR_SUBJECT_LINE', 'System Error')

    # Setup an SMTP mail handler for error-level messages
    from logging.handlers import SMTPHandler

    mail_handler = SMTPHandler(
        mailhost=(host, port),  # Mail host and port
        fromaddr=from_addr,  # From address
        toaddrs=to_addr_list,  # To address
        subject=subject,  # Subject line
        credentials=(username, password),  # Credentials
        secure=secure,
    )
    mail_handler.setLevel(level)
    app.logger.addHandler(mail_handler)


def init_mysql_handler(app, level):
    # logger setting
    import logging
    import mySQLHandler
    logger = logging.getLogger('wuaiwow')
    logger.setLevel(logging.DEBUG if app.debug else logging.WARNING)
    handler = mySQLHandler.mySQLHandler(db=app.config["DB"])
    handler.setLevel(level)
    app.logger.addHandler(handler)
    return logger


def gen_rnd_string(n):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))


def _allowed_file(file_obj, ext):
    import imghdr
    what = imghdr.what(file_obj)
    return imghdr.what(file_obj) in ext


def _save_file(file_obj, file_path):
    if file_obj:
        # 检查路径是否存在，不存在则创建
        dir_name = os.path.dirname(file_path)
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name)
            except:
                raise Exception('ERROR_CREATE_DIR')
        elif not os.access(dir_name, os.W_OK):
            raise Exception('ERROR_DIR_NOT_WRITEABLE')

        file_obj.save(file_path)


def save_file_upload(file_obj, exts, prefix):
    if file_obj and _allowed_file(file_obj, exts):
        filename = secure_filename(file_obj.filename)
        name, ext = os.path.splitext(filename)
        rnd_name = '%s%s' % (gen_rnd_string(10), ext)
        mid_path = os.path.join('uploads', datetime.datetime.now().strftime('%Y%m%d'))
        full_path = os.path.join(prefix, mid_path, rnd_name)

        # 保存文件
        try:
            _save_file(file_obj, full_path)
        except:
            raise
        else:
            return '%s/%s' % (mid_path, rnd_name)


def save_file_avatar(img, prefix):
    if img:
        rnd_name = '%s%s' % (gen_rnd_string(10), '.png')

        full_path = os.path.join(prefix, 'uploads/avatar', rnd_name)

        try:
            img.save(full_path)
        except:
            raise
        else:
            return '%s/%s' % ('uploads/avatar', rnd_name)


def resize_and_crop(img, size, position):
    """
    Resize and crop an image to fit the specified size.

    @param img: path or stream for the image to resize.
    @param size: `(width, height)` tuple.
    @param position: position of the box

    """
    # If height is higher we resize vertically, if not we resize horizontally
    img = Image.open(img)
    # Get current and desired ratio for the images
    img_ratio = img.size[0] / float(img.size[1])
    ratio = size[0] / float(size[1])
    # The image is scaled/cropped vertically or horizontally depending on the ratio
    if ratio > img_ratio:
        img = img.resize((size[0], int(round(size[0] * img.size[1] / img.size[0]))), Image.ANTIALIAS)
    elif ratio < img_ratio:
        img = img.resize((int(round(size[1] * img.size[0] / img.size[1])), size[1]), Image.ANTIALIAS)
    else:
        img = img.resize((size[0], size[1]), Image.ANTIALIAS)
    # Crop
    box = (position[0], position[1], position[0] + 100, position[1] + 100)
    img = img.crop(box)
    return img


__all__ = ['add_blueprint', 'configure_extensions', 'init_email_error_handler',
           'init_mysql_handler', 'gen_rnd_string', 'save_file_upload', 'save_file_avatar', 
           'resize_and_crop']
