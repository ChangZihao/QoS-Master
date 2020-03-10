import logging


def create_logger(name):
    # 创建flask.app日志器
    flask_logger = logging.getLogger(name)
    # 设置全局级别
    flask_logger.setLevel(logging.DEBUG)
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    # 给处理器设置输出格式
    console_formatter = logging.Formatter(
        fmt='[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s')
    console_handler.setFormatter(console_formatter)
    # 日志器添加处理器
    flask_logger.addHandler(console_handler)

    file_handler = logging.FileHandler('flask.log', encoding='UTF-8')
    file_handler.setFormatter(console_formatter)

    flask_logger.addHandler(file_handler)

    return flask_logger
