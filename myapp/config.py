import os

# 存放目录树的文件夹路径
file_path = 'myapp/file_tree.json'
# 获取环境变量的值
# 服务器密钥
secret_key = os.getenv('SECRET_KEY')
# 初始账户密码
init_username = os.getenv('USER_NAME')
init_password = os.getenv('PASSWORD')
# 图片根路径
root = 'myapp/static/images'
