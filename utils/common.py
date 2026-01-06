from configure.config import conf
from datetime import datetime
import pytz
import re

"""
본로직이 아닌 것들을 모음. 
1. KST 
"""

KST = pytz.timezone(conf.TIMEZONE)

def get_kst_now():
    """
    현재 시간을 KST(한국 시간)로 반환합니다.
    """
    return datetime.now(KST)



def normalize_ticker(ticker=None):
    """
    트레이딩뷰에서 오는 종목명을 정규화합니다.
    예: 'MNQ1!' -> 'MNQ',
    'G1C1!' -> 'GC',
    '@NQ(1)!' -> 'NQ'
    """
    if not ticker:
        return None
    # 숫자와 특수문자 제거 (예: 'MNQ1!' -> 'MNQ')

    normalized = re.sub(r'[0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', '', ticker).upper()
    return normalized


if __name__ == "__main__":
    print("#" * 100)
    print("# timezone test")
    print(conf.TIMEZONE)
    print(get_kst_now())
    print("\n")
    print("#" * 100)
    print("# normalize_ticker test ")
    for wd in ['MNQ1!', 'G1C1!', '@NQ(1)!']:
        print(f"{wd:15} => {normalize_ticker(wd)}")

