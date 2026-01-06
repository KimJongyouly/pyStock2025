import os
from pathlib import Path
from configure.config import conf, ROOT_DIR
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 경로 초기화
LOG_DIR = f"{ROOT_DIR}{os.sep}{conf.LOG_DIR}"
Path(LOG_DIR).mkdir(parents=True, exist_ok=True)  # 없으면 만들고

def setup_logging(app):
    """
    요건 앱을 위한 설정임.
    """
    # formater
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]: %(message)s')
    max_size = int(conf.LOG_SIZE) * 1024 * 1024
    backup_count = int(conf.BACKP_COUNT)

    for log_file, level in [(conf.INFO_LOG, logging.INFO), (conf.ERROR_LOG, logging.ERROR)]:
        handler = RotatingFileHandler(Path(LOG_DIR) / log_file,
                                      maxBytes=max_size,
                                      backupCount=backup_count,
                                      encoding='utf-8')
        handler.setFormatter(formatter)
        handler.setLevel(level)
        app.logger.addHandler(handler)

    # 전체 로깅 레벨을 INFO로 설정해야 두 핸들러 모두 작동함
    app.logger.setLevel(logging.INFO)
    app.logger.info("Logging setup completed: INFO and ERROR handlers added.")


def get_logger(name=None):
    """
    Flask 외부 모듈에서도 동일한 설정으로 로그를 남길 수 있게
    """
    logger = logging.getLogger(name or "pyStock")

    # 핸들러가 이미 추가되어 있다면 중복 방지를 위해 그대로 반환
    if logger.handlers:
        return logger

    # 기존 setup_logging에서 사용한 설정과 동일하게 구성
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]: %(message)s')
    max_size = int(conf.LOG_SIZE) * 1024 * 1024
    backup_count = int(conf.BACKP_COUNT)

    # INFO & ERROR 핸들러 추가
    for log_file, level in [(conf.INFO_LOG, logging.INFO), (conf.ERROR_LOG, logging.ERROR)]:
        handler = RotatingFileHandler(Path(LOG_DIR) / log_file,
                                      maxBytes=max_size,
                                      backupCount=backup_count,
                                      encoding='utf-8')
        handler.setFormatter(formatter)
        handler.setLevel(level)
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    return logger


if __name__ == "__main__":
    print(LOG_DIR)
