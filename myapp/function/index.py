import re
from flask import Blueprint, request, render_template, send_from_directory, g
from flask_login import login_required
import myapp
from myapp import diskio
from myapp.config import root
from myapp.function.basic import app_logger
import os


index_blueprint = Blueprint('index', __name__)

@index_blueprint.route('/', defaults={'url_path': ''})
@index_blueprint.route('/<path:url_path>')
@login_required
def index(url_path):
    """
    文件夹查看路由，展示文件夹内容或直接返回文件
    """
    from_viewer = request.args.get('from_viewer', default= 'false').lower() == 'true'
    path = re.split(r'\?', url_path)[0]

    if diskio.is_directory(path):
        # 如果不是来自浏览器的调用,清空统计
        if not from_viewer:
            myapp.blacklisted_directories = set()
        items = diskio.get_directory_contents(path)
        app_logger.debug(f'要访问的是{path},读取到的文件夹列表是{items}')
        return render_template('index.html', items=items, from_viewer=from_viewer, timestamp=myapp.SERVER_START_TIMESTAMP , nonce=g.nonce)
    else:
        # 转换为绝对路径
        absolute_root = os.path.abspath(root)
        app_logger.debug(f'要访问的是一个文件:{path},root的绝对路径是{absolute_root}')
        return send_from_directory(absolute_root, path)
    pass