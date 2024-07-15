import logging
from logging.handlers import TimedRotatingFileHandler
import os

# 创建一个 logger
logger = logging.getLogger("user")
logger.setLevel(logging.INFO)

# 创建一个 handler，用于写入日志文件
# midnight: 表示日志文件在每天半夜时分滚动
# interval: 间隔时间单位的个数，指等待多少个 when 的时间后 Logger 会自动重建新闻继续进行日志记录
# backupCount: 表示日志文件的保留个数，假如为7，则会保留最近的7个日志文件
current_path = os.path.abspath(__file__)
# path = os.path.join(os.path.dirname(current_path), "logs", 'log.log')
path = os.path.join(os.path.dirname(current_path), "logs")
if not os.path.isdir(path):
    os.makedirs(path)
filename = os.path.join(path, 'log.log')
save_handler = TimedRotatingFileHandler(filename=filename, when="midnight", interval=1, backupCount=7)
save_handler.suffix = "%Y-%m-%d"  # 设置日志文件名的时间戳格式

# 创建一个 handler，用于输出到控制台
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # 设置 handler 级别为 INFO

# 创建一个 formatter，用于设置日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 设置 handler 的格式
save_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 为 logger 添加 handler
logger.addHandler(save_handler)
logger.addHandler(console_handler)

# 记录日志
# logger.info('This is a log info')
# logger.debug('Debugging')
# logger.warning('Warning exists')
# logger.error('Error!')
