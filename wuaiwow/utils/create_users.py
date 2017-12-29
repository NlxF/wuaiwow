# -*- coding: utf-8 -*-
import StringIO
from PIL import Image
from werkzeug.datastructures import FileStorage
from wuaiwow import app, db
from wuaiwow.utils.modelHelper import find_or_create_permission, find_or_create_user, get_role_by_name, create_role


def create_all_permissions():
    permissions = []
    for idx, role in enumerate(app.config['PERMISSIONS']):
        role_obj = get_role_by_name(role=role[1])
        if not role_obj:
            role_obj = create_role(role=role[1], label=role[2])
        created, ps = find_or_create_permission(value=role[0], need_created=True, role=role_obj)
        permissions.append(ps)
    return permissions


def create_users():
    """ Create users when app starts """

    # Create all tables
    db.create_all()

    perms = create_all_permissions()

    # add default users
    user = find_or_create_user(u'luffy', u'wuaiwow@gmail.com', '123456', perms[-1].value)
    user = find_or_create_user(u'gm', u'825518250@qq.com', '123456', perms[-3].value)
    user = find_or_create_user(u'Zoro', u'it1780@sina.com', '123456', perms[0].value)

    # Save to DB
    db.session.commit()


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
