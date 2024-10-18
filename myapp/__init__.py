from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import time
from myapp.function.disk_io import DiskIO
from myapp.config import file_path, root, secret_key

print('开始读取文件构建目录树，请等待')
diskio = DiskIO(file_path, root)
print('成功构建目录树')
# 记录服务器启动时间戳
SERVER_START_TIMESTAMP = str(int(time.time()))
# 记录已经轮播的目录
blacklisted_directories = set()


db = SQLAlchemy()
def create_app():
    # 初始化 Flask 应用
    app = Flask(__name__)
    app.secret_key = secret_key
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60 * 60 * 24 * 7  # 缓存一周
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # 初始化数据库
    db.init_app(app)
    return app

# 用户模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    # example
    @classmethod
    def get(cls, username):
        return cls.query.filter_by(username=username).first()
