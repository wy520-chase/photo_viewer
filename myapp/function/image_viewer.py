import json
import os
import re
from pathlib import Path
from flask import Blueprint, request, render_template, jsonify, g
from flask_login import login_required
import myapp
from myapp import diskio, SERVER_START_TIMESTAMP
from myapp.function.basic import app_logger

image_viewer_blueprint = Blueprint('image_viewer', __name__)

@image_viewer_blueprint.route('/image_viewer')
@login_required
def image_viewer():
    """
    图片查看路由，传递当前文件夹下所有图片的信息，参数image_path是相对root的路径，不带static/images
    """
    url_field = request.args.get('image_path')
    app_logger.debug(f'图片查看器获取到的参数{url_field}')

    # 获取路径部分
    image_path = re.split(r'\?', url_field)[0]
    # 获取文件所在目录的路径
    directory_path = os.path.dirname(image_path)
    app_logger.debug(f'从图片{image_path}计算出的所在目录是{directory_path}')
    if directory_path:
        folder_name = os.path.basename(directory_path)
    else:
        folder_name = 'images'
    # 获取当前文件夹下的所有图片,images_info 是一个列表，每个元素是一个元组，元组第一个元素是文件名，第二个元素是文件路径
    images_info = diskio.get_directory_images(directory_path)
    app_logger.debug(f'获取路径{directory_path}下的所有图片:{images_info}')
    # 获取当前文件夹下的所有图片路径
    images_path = [image_path for _, image_path in images_info]
    # 获取当前图片索引
    try:
        image_id = images_path.index(image_path)
    except ValueError:
        image_id = 0

    images_json = json.dumps(images_path)
    # app_logger.debug(f'图片查看器传递信息：current_image_index={image_id},images_json={images_json}, folder_name={folder_name}')
    return render_template('image_viewer.html', images_json=images_json, folder_name=folder_name,
                           current_image_index=image_id, timestamp=SERVER_START_TIMESTAMP, nonce=g.nonce)

@image_viewer_blueprint.route('/image_viewer_recursively', methods=['GET'])
@login_required
def image_viewer_recursively():
    current_path = Path(request.args.get('current_path'))
    carousel_fps = request.args.get('carousel_fps')
    carousing = request.args.get('Carousing', default= 'false').lower() == 'true'
    app_logger.debug(f'current_path:{current_path}, carousing:{carousing}, carousel_fps:{carousel_fps}')
    # 获取当前图片所在目录
    current_directory = current_path.as_posix()
    myapp.blacklisted_directories.add(current_directory)
    # 传入当前目录和一个禁止目录列表，返回当前目录下的一个不在禁止目录列表且有图片的子目录路径，如果没有找到，把查找过的目录加黑名单
    # 返回当前目录的兄弟目录下的一个不在禁止目录列表且有图片的子目录路径，如果还没有，加黑名单并返回父目录下的一个不在禁止目录列表且有图片的子目录路径，依次类推
    result,myapp.blacklisted_directories  = diskio.find_new_images_in_directory(current_directory,myapp.blacklisted_directories)
    if result['images']:
        images_json = json.dumps(result['images'])
        # app_logger.debug(f"来自image_viewer_recursively函数:folder_name:{result['directory']},images_json: {images_json}")
        return render_template('image_viewer.html', images_json=images_json, folder_name=result['directory'],
                           current_image_index=0, timestamp=SERVER_START_TIMESTAMP, carousel_fps=carousel_fps, carousing = carousing, nonce=g.nonce)
    else:
        return jsonify({"message": "No images found in parent or sibling directories"}), 404
