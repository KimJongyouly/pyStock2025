import requests
import aiohttp
from configure.config import conf
from utils.mylogs import get_logger

logger = get_logger("Alarm")   # 작은 부분까지 확장이가능하도록 app, 모듈에서 호출하는 부분을 분리함.

"""
notify하는 부분은  여러 사항으로 확장이 가능한 부분이라 따로 분류 시킴. (=혹시나 확장이 될까?) 
    - sms : sms, lms, mms 
    - messenger : slack, telegram, (kakao, line :: 요건 이제 유료화됨) 
    - mail 
    
"""

class ctelegram:
    """
    alarm : telegram 전송
    """
    def __init__(self):
        self.url = conf.TELEGRAM_URL.format(TELEGRAM_TOKEN=conf.TELEGRAM_TOKEN)
        self.chat_id = conf.TELEGRAM_CHAT_ID

    def send(self, message):
        try:
            data = {'chat_id': self.chat_id, 'text': message}
            response = requests.post(self.url, data=data)
            if response.status_code != 200:
                 logger.error(f"텔레그램 전송 실패: {response.text}")
        except Exception as e:
            logger.error(f"텔레그램 전송 중 에러: {e}")

    async def async_send(self, message):
        try:
            data = {'chat_id': self.chat_id, 'text': message}
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, data=data) as response:
                    if response.status != 200:
                        logger.error(f"텔레그램 전송 실패: {await response.text()}")
        except Exception as e:
            logger.error(f"텔레그램 전송 중 에러: {e}")


if __name__ == "__main__":
    obj_telegram = ctelegram()  # 개체선언
    obj_telegram.init()
    obj_telegram.send('test')   # 메시지 보내기
