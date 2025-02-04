from flask import Blueprint, render_template, redirect, request, jsonify
from flask_login import login_required
import urllib.parse
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
    # 对 random_path 进行 URL 编码
    encoded_random_path = urllib.parse.quote(random_path)
    return redirect(f'/{random_path}')


delete_blueprint = Blueprint('delete_blueprint', __name__)
@delete_blueprint.route('/delete', methods=['POST'])
@login_required
def delete():
    """
    删除路由，处理删除图像和删除目录的请求
    :return: JSON 格式的响应结果
    """
    data = request.get_json()
    if 'path' not in data:
        return jsonify(success=False, message='路径不存在'), 400
    path_relative_root = data['path']
    success = diskio.delete_item(path_relative_root)
    return jsonify(success=success)