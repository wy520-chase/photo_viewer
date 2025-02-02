from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
import myapp
from myapp import diskio

index_button_blueprint = Blueprint('index_button', __name__)
@index_button_blueprint.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@index_button_blueprint.route('/random')
@login_required
def random():
    random_path = diskio.random_dir()
    return redirect(url_for('index.index', path=random_path))
