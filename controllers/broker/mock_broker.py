"""
Mock Broker Module - 가상 매매(Paper Trading) 기능
Tradovate API 대신 사용하는 시뮬레이션 브로커
주문을 받아서 CSV 파일에 기록합니다.

지금은 MockBroker를 사용하고 있지 않음.
"""

import csv
import os
from datetime import datetime
from typing import Dict, Optional


class MockBroker:
    """가상 매매 브로커 클래스"""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Args:
            log_dir: 로그 파일을 저장할 디렉토리 경로
        """
        self.log_dir = log_dir
        self.csv_file = os.path.join(log_dir, "trades.csv")
        
        # logs 디렉토리가 없으면 생성
        os.makedirs(log_dir, exist_ok=True)
        
        # CSV 파일이 없으면 헤더 작성
        if not os.path.exists(self.csv_file):
            self._initialize_csv()
    
    def _initialize_csv(self):
        """CSV 파일 초기화 (헤더 작성)"""
        with open(self.csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                '시간',
                '가격',
                '주문타입',
                '수량',
                '심볼',
                '상태'
            ])
    
    def place_order(
        self,
        order_type: str,
        price: float,
        symbol: str = "ES",
        quantity: int = 1,
        **kwargs
    ) -> Dict:
        """
        가상 주문을 실행하고 CSV에 기록합니다.
        
        Args:
            order_type: 주문 타입 (BUY, SELL, CLOSE 등)
            price: 주문 가격
            symbol: 거래 심볼 (기본값: ES)
            quantity: 수량 (기본값: 1)
            **kwargs: 추가 파라미터
        
        Returns:
            주문 결과 딕셔너리
        """
        # 현재 시간
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 주문 정보를 CSV에 저장
        self._log_trade(
            timestamp=timestamp,
            price=price,
            order_type=order_type,
            symbol=symbol,
            quantity=quantity
        )
        
        # 주문 결과 반환
        return {
            'status': 'success',
            'order_type': order_type,
            'price': price,
            'symbol': symbol,
            'quantity': quantity,
            'timestamp': timestamp,
            'message': f'가상 주문이 성공적으로 기록되었습니다: {order_type} {quantity} @ {price}'
        }
    
    def _log_trade(
        self,
        timestamp: str,
        price: float,
        order_type: str,
        symbol: str,
        quantity: int
    ):
        """거래 내역을 CSV 파일에 추가"""
        with open(self.csv_file, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                f'{price:.2f}',
                order_type,
                quantity,
                symbol,
                '완료'
            ])
    
    def get_trades(self) -> list:
        """
        저장된 모든 거래 내역을 읽어옵니다.
        
        Returns:
            거래 내역 리스트
        """
        if not os.path.exists(self.csv_file):
            return []
        
        trades = []
        with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                trades.append(row)
        
        return trades





