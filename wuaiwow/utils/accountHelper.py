# coding:utf-8
from flask import url_for
from functools import wraps
from flask import current_app
from flask.ext.login import current_user


def endpoint_url(endpoint):
    url = '/'
    if endpoint:
        url = url_for(endpoint)
    return url


def permission_required(permission_value):
    """ This decorator ensures that the current user has the specified permission.
        Calls the unauthorized_view_function() when requirements fail.
        See also: UserMixin.has_role()
        @param permission_value 操作要求的最低权限值
    """
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            # User must be logged
            if not _call_or_get(current_user.is_authenticated):
                # Redirect to the unauthenticated page
                return current_app.user_manager.unauthenticated_view_function()

            # User must have the required permission
            if not current_user.has_permission(permission_value):
                # Redirect to the unauthorized page
                return current_app.user_manager.unauthorized_view_function()

            # Call the actual view
            return func(*args, **kwargs)
        return decorated_view
    return wrapper


def _call_or_get(function_or_property):
    return function_or_property() if callable(function_or_property) else function_or_property