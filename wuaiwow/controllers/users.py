# coding:utf-8
from flask import current_app, flash, redirect, render_template, request, url_for, Blueprint, jsonify
from flask_login import login_user, logout_user
from flask_user import current_user, login_required, emails
from flask_user.signals import user_confirmed_email
from flask_user.decorators import confirm_email_required, login_required
from flask_user.forms import LoginForm
from flask_user.translations import gettext as _
from datetime import datetime
from wuaiwow import tasks
from wuaiwow import app, db, logger
from wuaiwow.utils import add_blueprint, save_file_avatar, resize_and_crop
from wuaiwow.utils.accountHelper import endpoint_url
from wuaiwow.utils.modelHelper import find_or_create_permission
from wuaiwow.utils.messageHelper import add_new_register_message, add_reset_password_message, add_change_password_message
try:
    from urllib.parse import quote      # Python 3.x
except ImportError:
    from urllib import quote            # Python 2.x


bp = Blueprint('users', __name__, url_prefix='/user')


@bp.route('register', methods=['GET', 'POST'])
def register():
    """ Display registration form and create new User.

    """
    user_manager = current_app.user_manager
    db_adapter = user_manager.db_adapter

    next = request.args.get('next', endpoint_url(user_manager.after_login_endpoint))
    reg_next = request.args.get('reg_next', endpoint_url(user_manager.after_register_endpoint))

    # Initialize form
    login_form = user_manager.login_form()                      # for login_or_register.html
    register_form = user_manager.register_form(request.form)    # for register.html

    # invite token used to determine validity of registeree
    invite_token = request.values.get("token")

    # require invite without a token should disallow the user from registering
    if user_manager.require_invitation and not invite_token:
        flash(_("Registration is invite only"), "error")
        return redirect(url_for('user.login'))

    user_invite = None
    if invite_token and db_adapter.UserInvitationClass:
        user_invite = db_adapter.find_first_object(db_adapter.UserInvitationClass, token=invite_token)
        if user_invite:
            register_form.invite_token.data = invite_token
        else:
            flash(_("Invalid invitation token"), "error")
            return redirect(url_for('user.login'))

    if request.method != 'POST':
        login_form.next.data     = register_form.next.data     = next
        login_form.reg_next.data = register_form.reg_next.data = reg_next
        if user_invite:
            register_form.email.data = user_invite.email

    # Process valid POST
    if request.method == 'POST' and register_form.validate():
        # Create a User object using Form fields that have a corresponding User field
        User = db_adapter.UserClass
        user_class_fields = User.__dict__
        user_fields = {}

        # Create a UserEmail object using Form fields that have a corresponding UserEmail field
        if db_adapter.UserEmailClass:
            UserEmail = db_adapter.UserEmailClass
            user_email_class_fields = UserEmail.__dict__
            user_email_fields = {}

        # Create a UserAuth object using Form fields that have a corresponding UserAuth field
        if db_adapter.UserAuthClass:
            UserAuth = db_adapter.UserAuthClass
            user_auth_class_fields = UserAuth.__dict__
            user_auth_fields = {}

        # Enable user account
        if db_adapter.UserProfileClass:
            if hasattr(db_adapter.UserProfileClass, 'active'):
                user_auth_fields['active'] = True
            elif hasattr(db_adapter.UserProfileClass, 'is_enabled'):
                user_auth_fields['is_enabled'] = True
            else:
                user_auth_fields['is_active'] = True
        else:
            if hasattr(db_adapter.UserClass, 'active'):
                user_fields['active'] = True
            elif hasattr(db_adapter.UserClass, 'is_enabled'):
                user_fields['is_enabled'] = True
            else:
                user_fields['is_active'] = True

        # For all form fields
        for field_name, field_value in register_form.data.items():
            # Hash password field
            if field_name == 'password':
                hashed_password = user_manager.hash_password(field_value)
                if db_adapter.UserAuthClass:
                    user_auth_fields['password'] = hashed_password
                else:
                    user_fields['password'] = hashed_password
            # Store corresponding Form fields into the User object and/or UserProfile object
            else:
                if field_name in user_class_fields:
                    user_fields[field_name] = field_value
                if db_adapter.UserEmailClass:
                    if field_name in user_email_class_fields:
                        user_email_fields[field_name] = field_value
                if db_adapter.UserAuthClass:
                    if field_name in user_auth_class_fields:
                        user_auth_fields[field_name] = field_value

        # Add User record using named arguments 'user_fields'
        user = db_adapter.add_object(User, **user_fields)
        created, user.permission = find_or_create_permission(10)
        if db_adapter.UserProfileClass:
            user_profile = user

        # Add UserEmail record using named arguments 'user_email_fields'
        if db_adapter.UserEmailClass:
            user_email = db_adapter.add_object(UserEmail,
                    user=user,
                    is_primary=True,
                    **user_email_fields)
        else:
            user_email = None

        # Add UserAuth record using named arguments 'user_auth_fields'
        if db_adapter.UserAuthClass:
            user_auth = db_adapter.add_object(UserAuth, **user_auth_fields)
            if db_adapter.UserProfileClass:
                user = user_auth
            else:
                user.user_auth = user_auth

        require_email_confirmation = True
        if user_invite:
            if user_invite.email == register_form.email.data:
                require_email_confirmation = False
                db_adapter.update_object(user, confirmed_at=datetime.utcnow())

        # Send 'registered' email and delete new User object if send fails
        if user_manager.send_registered_email:
            try:
                # Send create_account message to proxy_server, sync
                resp = tasks.create_account(user_fields['username'], register_form.data['password'])
                if resp[0]:
                    # Send 'registered' email
                    # _send_registered_email(user, user_email, require_email_confirmation)
                    db_adapter.commit()

                    # send register email async
                    tasks.send_registered_email(user, user_email, require_email_confirmation)

                    # Prepare one-time system message
                    if user_manager.enable_confirm_email and require_email_confirmation:
                        email = user_email.email if user_email else user.email
                        flash(_('A confirmation email has been sent to %(email)s with instructions to complete your registration.', email=email), 'success')
                    else:
                        flash(_('You have registered successfully.'), 'success')
                else:
                    msg = u"{0}:{1}".format("LServer", resp[-1])
                    flash(_(msg), category='error')
            except Exception as e:
                msg = u"{}:{}".format(e.args[0], unicode(e.args[-1]))
                logger.error(msg)
                flash(_("LServer:Create account failed."), category='error')
            else:
                if resp[0]:
                    # Redirect if USER_ENABLE_CONFIRM_EMAIL is set
                    if user_manager.enable_confirm_email and require_email_confirmation:
                        next = request.args.get('next', endpoint_url(user_manager.after_register_endpoint))
                        return redirect(next)

                    # Auto-login after register or redirect to login page
                    next = request.args.get('next', endpoint_url(user_manager.after_confirm_endpoint))
                    if user_manager.auto_login_after_register:
                        return _do_login_user(user, reg_next)                     # auto-login
                    else:
                        return redirect(url_for('user.login')+'?next='+reg_next)  # redirect to login page

    # Process GET or invalid POST
    return render_template(user_manager.register_template,
            form=register_form,
            login_form=login_form,
            register_form=register_form)


@bp.route('change-password', methods=['GET', 'POST'])
@login_required
@confirm_email_required
def change_password():
    """ Prompt for old password and new password and change the user's password."""
    user_manager = current_app.user_manager
    db_adapter = user_manager.db_adapter

    # Initialize form
    form = user_manager.change_password_form(request.form)
    form.next.data = request.args.get('next', endpoint_url(user_manager.after_change_password_endpoint))  # Place ?next query param in next form field

    # Process valid POST
    if request.method == 'POST' and form.validate():
        # Hash password
        hashed_password = user_manager.hash_password(form.new_password.data)

        try:
            resp = tasks.change_pwd(current_user.username, form.new_password.data)
            if not resp[0]:
                flash(_("lserver:change password fail"), category='error')
        except Exception, e:
            flash(_("lserver:change password fail"), category='error')
        else:
            if resp[0]:
                # Change password
                user_manager.update_password(current_user, hashed_password)

                # Send 'password_changed' email
                if user_manager.enable_email and user_manager.send_password_changed_email:
                    emails.send_password_changed_email(current_user)

                # Send password_changed signal
                # signals.user_changed_password.send(current_app._get_current_object(), user=current_user)

                # Prepare one-time system message
                # flash(_('Your password has been changed successfully.'), 'success')
                add_change_password_message(current_user)

                # Redirect to 'next' URL
                return redirect(form.next.data)

    # Process GET or invalid POST
    return render_template(user_manager.change_password_template, form=form, user=current_user)


@user_confirmed_email.connect_via(app)
def active_use(sender, user, **extra):
    try:
        resp = tasks.active_account(user.username)
        if not resp[0]:
            flash(_("lserver:account activation failed"), 'error')
    except Exception, e:
        flash(_("lserver:Account activation failed"), 'error')
    else:
        # flash(_('account activation succeeded'))
        add_new_register_message(user)


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """ Verify the password reset token, Prompt for new password, and set the user's password."""
    # Verify token
    user_manager = current_app.user_manager
    db_adapter = user_manager.db_adapter

    if _call_or_get(current_user.is_authenticated):
        logout_user()

    is_valid, has_expired, user_id = user_manager.verify_token(
            token,
            user_manager.reset_password_expiration)

    if has_expired:
        flash(_('Your reset password token has expired.'), 'error')
        return redirect(url_for('user.login'))

    if not is_valid:
        flash(_('Your reset password token is invalid.'), 'error')
        return redirect(url_for('user.login'))

    user = user_manager.get_user_by_id(user_id)
    if user:
        # Avoid re-using old tokens
        if hasattr(user, 'reset_password_token'):
            verified = user.reset_password_token == token
        else:
            verified = True
    if not user or not verified:
        flash(_('Your reset password token is invalid.'), 'error')
        return redirect(endpoint_url(user_manager.login_endpoint))

    # Mark email as confirmed
    user_email = emails.get_primary_user_email(user)
    user_email.confirmed_at = datetime.utcnow()

    # Initialize form
    form = user_manager.reset_password_form(request.form)

    # Process valid POST
    if request.method=='POST' and form.validate():
        # Invalidate the token by clearing the stored token
        if hasattr(user, 'reset_password_token'):
            db_adapter.update_object(user, reset_password_token='')

        # Change password
        try:
            tasks.change_pwd(user.username, form.new_password.data)
        except Exception, e:
            flash(_('lserver:reset password failed'), category='error')
            # raise
        else:
            hashed_password = user_manager.hash_password(form.new_password.data)
            user_auth = user.user_auth if db_adapter.UserAuthClass and hasattr(user, 'user_auth') else user
            db_adapter.update_object(user_auth, password=hashed_password)
            db_adapter.commit()

            # Send 'password_changed' email
            if user_manager.enable_email and user_manager.send_password_changed_email:
                emails.send_password_changed_email(user)

            # Prepare one-time system message
            # flash(_("Your password has been reset successfully."), 'success')
            add_reset_password_message(current_user)

            # Auto-login after reset password or redirect to login page
            next = request.args.get('next', endpoint_url(user_manager.after_reset_password_endpoint))
            if user_manager.auto_login_after_reset_password:
                return _do_login_user(user, next)                       # auto-login
            else:
                return redirect(url_for('user.login')+'?next='+next)    # redirect to login page

        return render_template(user_manager.reset_password_template, form=form)

    # Process GET or invalid POST
    return render_template(user_manager.reset_password_template, form=form)


@bp.route('/avatar/upload/', methods=['POST', ])
@login_required
@confirm_email_required
def user_avatar():
    if request.method == 'POST':
        user = current_user
        if request.files and request.files['picture']:
            f = request.files['picture']
            result = {'status': 'Err', 'msg': u'头像修改失败'}
            if request.form and isinstance(request.form['size'], basestring):
                try:
                    size = [int(x) for x in request.form['size'].split(',')]
                    f = resize_and_crop(f, size[0:2], size[2:])
                    file_name = save_file_avatar(f, app.static_folder)
                    avatar_url = url_for('static', filename=file_name)
                except Exception, e:
                    pass
                else:
                    user.avatar = avatar_url
                    db.session.add(user)
                    db.session.commit()
                    result = {'status': 'Ok', 'msg': u'头像修改成功', 'avatar_url': avatar_url}
            return jsonify(result)

    return redirect('/user/profile#avatar')


# def _send_registered_email(user, user_email, require_email_confirmation=True):
#     user_manager = current_app.user_manager
#     db_adapter = user_manager.db_adapter
#
#     # Send 'confirm_email' or 'registered' email
#     if user_manager.enable_email and user_manager.enable_confirm_email:
#         # Generate confirm email link
#         object_id = user_email.id if user_email else int(user.get_id())
#         token = user_manager.generate_token(object_id)
#         confirm_email_link = url_for('user.confirm_email', token=token, _external=True)
#
#         # Send email
#         emails.send_registered_email(user, user_email, confirm_email_link)
#
#         # Prepare one-time system message
#         if user_manager.enable_confirm_email and require_email_confirmation:
#             email = user_email.email if user_email else user.email
#             flash(_('A confirmation email has been sent to %(email)s with instructions to complete your registration.', email=email), 'success')
#         else:
#             flash(_('You have registered successfully.'), 'success')


def unauthenticated():
    """ Prepare a Flash message and redirect to USER_UNAUTHENTICATED_ENDPOINT"""
    # Prepare Flash message
    url = request.url
    flash(_("You must be signed in to access '%(url)s'.", url=url), 'error')

    # quote the fully qualified url
    quoted_url = quote(url)

    # Redirect to USER_UNAUTHENTICATED_ENDPOINT
    user_manager = current_app.user_manager
    return redirect(endpoint_url(user_manager.unauthenticated_endpoint)+'?next='+ quoted_url)


def _call_or_get(function_or_property):
    return function_or_property() if callable(function_or_property) else function_or_property


def _do_login_user(user, next, remember_me=False):
    # User must have been authenticated
    if not user: return unauthenticated()

    # Check if user account has been disabled
    if not _call_or_get(user.is_active):
        flash(_('Your account has not been enabled.'), 'error')
        return redirect(url_for('user.login'))

    # Check if user has a confirmed email address
    user_manager = current_app.user_manager
    if user_manager.enable_email and user_manager.enable_confirm_email \
            and not current_app.user_manager.enable_login_without_confirm_email \
            and not user.has_confirmed_email():
        url = url_for('user.resend_confirm_email')
        flash(_('Your email address has not yet been confirmed. Check your email Inbox and Spam folders for the confirmation email or <a href="%(url)s">Re-send confirmation email</a>.', url=url), 'error')
        return redirect(url_for('user.login'))

    # Use Flask-Login to sign in user
    # print('login_user: remember_me=', remember_me)
    login_user(user, remember=remember_me)

    # Prepare one-time system message
    flash(_('You have signed in successfully.'), 'success')

    # Redirect to 'next' URL
    return redirect(next)


# Register blueprint
add_blueprint(bp)
