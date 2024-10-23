from flask import Blueprint, redirect, url_for, flash, request, render_template
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from myapp import User
from myapp.function.basic import app_logger

login_blueprint = Blueprint('login', __name__)

@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    app_logger.info('login')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.get(username)
        if user and check_password_hash(user.password, password):
            login_user(user)  # 登录用户
            flash('Logged in successfully.')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index.index'))  # 正确的重定向目标
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@login_blueprint.route('/logout')
def logout():
    logout_user()  # 注销用户
    flash('Logged out successfully.')
    return redirect(url_for('login.login'))  # 重定向到登录页面



