# -*- coding: utf-8 -*-
from flask_user.forms import RegisterForm, LoginForm, ChangePasswordForm


class MyRegisterForm(RegisterForm):
    pass


class MyLoginForm(LoginForm):
    pass


class MyChangePasswordForm(ChangePasswordForm):
    pass
