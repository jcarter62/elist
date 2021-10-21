from flask import Blueprint, render_template, redirect, request, session
from appsettings import AppSettings
from .db import DB as AuthDB
from session_info import Session_Info
from password_validator import PasswordValidator

auth_routes = Blueprint('auth_routes', __name__, static_folder='static', template_folder='templates')


@auth_routes.route('/login', methods=['GET'])
def route_login():
    context = {
        "title": "Login",
        'session': Session_Info().data
    }
    return render_template('login.html', context=context)


@auth_routes.route('/login', methods=['POST'])
def route_login_post():
    username = request.form['username']
    pw = request.form['password']

    authdb = AuthDB()
    data = authdb.load_record(username=username, password=pw)
    if data is None:
        #
        # login failed, so they need to login again
        #
        return redirect('/auth/login')
    else:
        #
        # login success, so save session info.
        #
        session['user_id'] = data['id']
        session['authenticated'] = True
        session['username'] = data['username']
        session['email'] = data['email']
        session['admin'] = data['admin']
        #
        return redirect('/')


@auth_routes.route('/login-create', methods=['GET'])
def route_login_create():
    context = {
        "title": "Login - Create Account",
        "username": '',
        "pw1": '',
        "pw2": '',
        "feedback": '',
        'session': Session_Info().data
    }
    return render_template('login-create.html', context=context)


@auth_routes.route('/login-create', methods=['POST'])
def route_login_create_post():
    username = request.form['username']
    pw = request.form['password']
    pw2 = request.form['password2']

    if pw == pw2:
        authdb = AuthDB()
        data = authdb.insert_record(username=username, password=pw)
        return redirect('/auth/login')
    else:
        context = {
            "title": "Login - Create Account",
            "username": username,
            "pw1": pw,
            "pw2": pw2,
            "feedback": 'passwords did not match',
            'session': Session_Info().data
        }
        return render_template('login-create.html', context=context)


@auth_routes.route('/logout', methods=['GET'])
def route_logout():
    for key in list(session.keys()):
        session.pop(key)

    return redirect('/')


@auth_routes.route('/profile-edit/<user_id>', methods=['GET'])
def route_profile_edit(user_id):
    if Session_Info().matches_id(user_id):
        authdb = AuthDB()
        data = authdb.load_profile_record(user_id)
        context = {
            "title": "Edit Profile",
            "data": data,
            'session': Session_Info().data
        }
        return render_template('profile-edit.html', context=context)
    else:
        return redirect('/')


@auth_routes.route('/profile-edit', methods=['POST'])
def route_profile_edit_post():
    btn = request.form['btn']
    user_id = request.form['user_id']

    if Session_Info().matches_id(user_id):
        if btn == 'update':
            username = request.form['username']
            email = request.form['email']
            authdb = AuthDB()
            authdb.update_profile_record(user_id, username, email)
            url = '/auth/profile-edit/' + user_id
            return redirect(url)
        elif btn == 'pwchange':
            data = {
                'user_id': user_id,
                'password': '',
                'pass1': '',
                'pass2': '',
                'message': ''
            }
            context = {
                "title": "Edit Profile",
                "data": data,
                'session': Session_Info().data
            }
            return render_template('change-password.html', context=context)
    else:
        return redirect('/')


@auth_routes.route('/change-password', methods=['POST'])
def route_profile_change_password():
    user_id = request.form['user_id']
    if Session_Info().matches_id(user_id):
        hwhap = False
        password = request.form['curr_pass']
        pass1 = request.form['new_pass1']
        pass2 = request.form['new_pass2']
        message = ''
        # determine if current password is correct.
        authdb = AuthDB(user_id=user_id)
        if not authdb.is_correct_password(password=password):
            hwhap = True
            message += 'Password is not correct. '
        # determine if pass1 and pass2 match
        if not hwhap:
            if ( pass1 != pass2 ):
                hwhap = True
                message += 'Passwords do not match. '

        # determine if pass1 is complex
        if not hwhap:
            if isNotComplex(pass1):
                hwhap = True
                message += 'Password too simple.'

        if hwhap:
            data = {
                'user_id': user_id,
                'password': password,
                'pass1': pass1,
                'pass2': pass2,
                'message': message
            }
            context = {
                "title": "Edit Profile",
                "data": data,
                'session': Session_Info().data
            }
            return render_template('change-password.html', context=context)

        # all is good, go ahead and save new password.
        authdb = AuthDB()
        authdb.save_password(user_id, pass1)
        url = '/auth/logout'
        return redirect(url)
    else:
        return redirect('/')


# ref: https://pypi.org/project/password-validator/
#
def isNotComplex(pwd) -> bool:
    schema = PasswordValidator()

    schema.min(10)
    schema.max(50)
    schema.has().lowercase()
    schema.has().digits()

    result = not schema.validate(pwd)
    return result

