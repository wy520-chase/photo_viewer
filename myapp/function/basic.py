import logging

# 日志记录
# 创建一个新的日志记录器
app_logger = logging.getLogger('app_logger')
app_logger.setLevel(logging.INFO)

# 创建文件处理器
file_handler = logging.FileHandler('myapp/app.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# 设置日志格式
formatter = logging.Formatter('%(asctime)s - 来自%(funcName)s函数 - %(message)s')
file_handler.setFormatter(formatter)

# 添加文件处理器到日志记录器
app_logger.addHandler(file_handler)