# coding: utf-8
from sqlalchemy.sql import func
from sqlalchemy.orm import load_only
from .modelHelper import get_permission_by_role


def template_by_role(user, *templates):
    """根据用户Role返回模板名

    @param user 用户
    @param templates 模板列表, 按权限顺序升级

    """
    template_name = ''
    if user and len(templates):
        if user.has_permission(get_permission_by_role('UPGRADE')):
            template_name = templates[-1]
        elif user.has_permission(get_permission_by_role('GM')):
            template_name = templates[0] if len(templates) == 2 else templates[1]
        else:
            template_name = templates[0]
    return template_name


def _optimized_random(model_name):
    from wuaiwow import db
    return model_name.query.options(load_only('id')).offset(
            func.floor(
                func.random() *
                db.session.query(func.count(model_name.id))
            )
        ).limit(1).all()


def random_prompt(prompt_model, field=None):
    prompt = ''
    if prompt_model:
        if field:
            row = prompt_model.query.order_by(func.random()).filter_by(alive=field).first()
        else:
            row = prompt_model.query.order_by(func.random()).first()
        prompt = row.prompt if row else ' '
    return prompt


def all_prompt(prompt_model):
    pts = []
    if prompt_model:
        rows = prompt_model.query.order_by(prompt_model.id.asc())
        for row in rows:
            pts.append(row.prompt)
    return pts
