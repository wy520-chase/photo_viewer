from flask import jsonify, make_response
import time
from flask_login import LoginManager
from werkzeug.exceptions import BadRequest
from werkzeug.security import generate_password_hash
from myapp.config import init_username, init_password
from myapp import create_app, db, User
from myapp.function.basic import app_logger

app = create_app()
# 初始化数据库，创建初始账户
with app.app_context():
    db.create_all()
    # 加密密码
    hashed_password = generate_password_hash(init_password)
    # 检查用户是否已经存在，避免重复插入
    if not User.query.filter_by(username=init_username).first():
        initial_user = User(username=init_username, password=hashed_password)
        db.session.add(initial_user)
        db.session.commit()
        app_logger.debug(f"User '{init_username}' created with hashed password.")
    else:
        app_logger.debug(f"User '{init_username}' already exists.")

# 配置图片的缓存控制头
@app.after_request
def add_cache_control_headers(response):
    """
    在每个响应返回给客户端之前，向图片响应添加缓存控制头。
    该函数作为 Flask 的请求后处理钩子函数 (after_request)，
    目的是为了优化图片资源的缓存管理。

    参数:
    response (Response): Flask 的响应对象。
    返回:
    Response: 修改后的响应对象。
    """
    if response.mimetype.startswith('image'):
        # 设置Cache-Control头，图片资源公开缓存，有效期为一年，并且表示资源是不可变的
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        # 设置Expires头，为当前时间加上一年的秒数
        response.headers['Expires'] = int(time.time()) + 31536000
        # 设置ETag头，用于资源的缓存校验，避免不必要的下载
        response.headers['ETag'] = response.get_etag()[0]
    return response

# 设置 Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.login'
# 用户加载函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 异常处理
@app.errorhandler(BadRequest)
def handle_bad_request(e):
    response = jsonify({"error": "Bad Request", "message": str(e)})
    return make_response(response, 400)

# 登录蓝图
from myapp.function.login import login_blueprint
app.register_blueprint(login_blueprint)

# 主页蓝图
from myapp.function.index import index_blueprint
app.register_blueprint(index_blueprint)

# 图片查看页面
from myapp.function.image_viewer import image_viewer_blueprint
app.register_blueprint(image_viewer_blueprint)

# 设置界面
from myapp.function.settings import settings_blueprint
app.register_blueprint(settings_blueprint)

# 删除功能
from myapp.function.disk_io import delete_blueprint
app.register_blueprint(delete_blueprint)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

