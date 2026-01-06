from pathlib import Path
from dotenv import dotenv_values

"""
설정 파일 : 
Tradovate API 설정은 제거하고, Paper Trading에 필요한 설정만 유지합니다.
dotenv를 사용한다면 dotenv를 적극적으로 사용 
"""

class Config:
    """
    .env에서 읽어온 setting value는 {key : value, ....}의 형식임.
    이러한 value에 대한 접근, 은닉을 위한 개체를 하나 만듦.
    """
    def __init__(self, entries):
        self.__dict__.update(entries)


ROOT_DIR = Path(__file__).resolve().parent.parent
settings = dotenv_values(f"{ROOT_DIR}/.env")
conf = Config(settings)


if __name__ == "__main__":
    """
    value 확인용 
    Cd configure 
    python config.py 라고 하면 아래의 value들이 출력됨. 
    """
    print(ROOT_DIR)
    if conf.FLASK_DEBUG.lower() == 'true':
        for k, v in settings.items():
            print(f"{k:<16} => {v}")
