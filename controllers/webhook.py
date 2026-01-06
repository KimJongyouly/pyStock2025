from flask import jsonify
from datasource.dao import rdb
from utils.common import get_kst_now, normalize_ticker
from configure.config import conf
from utils.notify import ctelegram


def log_trade(app, ticker, order, price, quantity, reason):
    """
    trades.db insert
    """
    obj_telegram = ctelegram()
    db_sqlite = rdb()
    db_sqlite.connect()

    sql = {"insert": """INSERT INTO trades(dt,stock_cd, order, price, quantity, reason)
                      VALUES ('{dt}', '{ticker}', '{order}', {price}, {quantity}, '{reason}')
                      """, }

    dt = get_kst_now().strftime('%Y-%m-%d %H:%M:%S')
    insert_sql = sql['insert'].format(dt=dt,
                                      ticker=ticker,
                                      order=order,
                                      price=price,
                                      quantity=quantity,
                                      reason=reason)
    # debug mode이면 화면에 바로 출력
    if conf.FLASK_DEBUG.lower() == 'true':
        print(insert_sql)

    # db insert
    db_sqlite.insert(insert_sql)

    # log_writer
    log_msg = f"[매매 체결] {ticker} {order} @ {price} | 수량: {quantity}, 사유: {reason}"
    app.logger.info(log_msg)

    # send
    obj_telegram.send(f"[자동매매 알림]\n\n종목: {ticker}\n주문: {order}\n가격: {price}\n수량: {quantity}\n시간: {dt}\n사유: {reason}")
    app.logger.info("텔레그램 알림 전송 시도 완료")


def send_status_report(app, ticker,
                             current_price,
                             current_macd,
                             prev_macd,
                             signal_value,
                             is_touching,
                             conclusion):
    """
    현황 보고 알림을 텔레그램으로 전송합니다.
    """
    obj_telegram = ctelegram()
    timestamp = get_kst_now().strftime('%Y-%m-%d %H:%M:%S')
    touch_status = "일목터치(O)" if is_touching else "일목터치(X)"

    # MACD 비교 정보 구성
    if prev_macd is not None:
        macd_info = f"현재MACD: {current_macd:.4f}\n이전MACD: {prev_macd:.4f}"
    else:
        macd_info = f"현재MACD: {current_macd:.4f}\n이전MACD: (초기화 중)"

    if signal_value is not None:
        macd_info += f"\n시그널: {signal_value:.4f}"

    # 약간 직관적일 같아 변경함.
    obj_telegram.send(f"""[{timestamp}] 현황보고 {ticker}

현재가격: {current_price:.2f}
{macd_info}
일목터치: {touch_status}

결론: {conclusion}""")
    app.logger.info(f"[{ticker}] 현황 보고 알림 전송 완료")


def handle_webhook(app, market_state, data):
    obj_telegram = ctelegram()
    db_sqlite = rdb()
    db_sqlite.connect()
    try:
        if data.get('secret') != conf.WEBHOOK_SECRET:
            return jsonify({'error': 'Unauthorized'}), 401

        msg_type = data.get('type')
        ticker = normalize_ticker(data.get('ticker'))

        if not ticker:
            return jsonify({'status': 'ignored', 'reason': 'Invalid ticker'}), 200

        # 새로운 종목 자동 등록
        if ticker not in market_state:
            market_state[ticker] = {} # Initialize if not exists
            market_state[ticker]['prev_macd'] = None
            market_state[ticker]['ichimoku'] = {}
            app.logger.info(f"새로운 종목 감지: {ticker} (자동 등록 완료)")

        ############################################################################################
        if msg_type and 'ICHIMOKU' in msg_type:   # [A] 일목균형표 데이터 수신
            # request하는 부분이 json이라면 이미 그 데이터에 대해 그대로 사용할 있는 형태로 했으면 어땠을까?
            market_state[ticker]['ichimoku'] = { 'tenkan': float(data.get('tenkan', 0)),
                                                 'kijun': float(data.get('kijun', 0)),
                                                 'chikou': float(data.get('chikou', 0)),
                                                 'senkou_a': float(data.get('senkou_a', 0)),
                                                 'senkou_b': float(data.get('senkou_b', 0))}

            # 이건 데이터로 넣는게 맞지 않을까?
            # 로그에 다음과 같은 글들이 계속 들어간다는 건 불필요하게 로그의 사이즈만 증가될 것 같음.
            app.logger.info(
                f"☁️ [{ticker}] 일목균형표 데이터 수신 | "
                f"전환선: {market_state[ticker]['ichimoku']['tenkan']:.2f}, "
                f"기준선: {market_state[ticker]['ichimoku']['kijun']:.2f}, "
                f"선행스팬A: {market_state[ticker]['ichimoku']['senkou_a']:.2f}, "
                f"선행스팬B: {market_state[ticker]['ichimoku']['senkou_b']:.2f}"
            )
            return jsonify({'status': 'success', 'msg': 'Ichimoku lines updated'}), 200

        ############################################################################################
        elif msg_type == 'MACD_REPORT':  # [B] MACD 데이터 수신 (매매 판단)
            # request하는 부분이 json이라면 이미 그 데이터에 대해 그대로 사용할 있는 형태로 했으면 어땠을까?
            current_macd = float(data.get('macd_value', 0))
            signal_value = float(data.get('signal_value', 0))
            candle_high = float(data.get('high', 0))
            candle_low = float(data.get('low', 0))
            current_price = float(data.get('close', 0))
            prev_macd = market_state[ticker].get('prev_macd') # Use .get for safety

            # MACD 데이터 수신 시 무조건 상세 로그 출력 (매매 신호와 무관하게)
            if prev_macd is None:
                app.logger.info(f"[{ticker}] MACD 데이터 수신 | " 
                                f"현재가격: {current_price:.2f}, "
                                f"현재MACD: {current_macd:.4f}, "
                                f"이전MACD: (초기화 중)")
                market_state[ticker]['prev_macd'] = current_macd
                app.logger.info(f"{ticker} MACD 초기화 완료: {current_macd:.4f}")
                # 일목균형표 데이터가 있으면 현황 보고 전송
                ichimoku = market_state[ticker].get('ichimoku', {{}})
                if ichimoku:
                    lines = [ichimoku.get('tenkan', 0), ichimoku.get('kijun', 0), ichimoku.get('chikou', 0), ichimoku.get('senkou_a', 0), ichimoku.get('senkou_b', 0)]
                    is_touching = any(candle_low <= line_val <= candle_high for line_val in lines)
                    send_status_report(app, ticker,
                                             current_price,
                                             current_macd,
                                             prev_macd,
                                             signal_value,
                                             is_touching,
                                       "대기 중 (MACD 초기화)")
                return jsonify({'status': 'init', 'msg': 'MACD initialized'}), 200

            # 이전 MACD 값이 있는 경우 상세 로그 출력
            app.logger.info(f"[{ticker}] MACD 데이터 수신 | 현재가격: {current_price:.2f}, 현재MACD: {current_macd:.4f}, 이전MACD: {prev_macd:.4f}")
            ichimoku = market_state[ticker].get('ichimoku', {{}})

            if not ichimoku:
                market_state[ticker]['prev_macd'] = current_macd
                app.logger.info(f"⏳ [{ticker}] 일목균형표 데이터 대기 중...")
                send_status_report(app, ticker,
                                         current_price,
                                         current_macd,
                                         prev_macd,
                                         signal_value,
                                         False,
                                   "대기 중 (일목균형표 데이터 없음)")
                return jsonify({'status': 'waiting', 'msg': 'No Ichimoku data'}), 200

            # 전략 로직
            lines = [ichimoku.get('tenkan', 0), ichimoku.get('kijun', 0), ichimoku.get('chikou', 0), ichimoku.get('senkou_a', 0), ichimoku.get('senkou_b', 0)]
            is_touching = False
            for line_val in lines:
                if candle_low <= line_val <= candle_high:
                    is_touching = True
                    break

            touch_msg = "일목터치(O)" if is_touching else "일목터치(X)"

            # 매수/매도 판단
            trade_executed = False
            if prev_macd < 0 and current_macd >= 0:  # 골든크로스
                app.logger.info(f"🔍 {ticker} MACD 골든크로스! ({touch_msg})")
                if is_touching:
                    log_trade(app, ticker, 'BUY', current_price, 1, 'MACD양전 + 일목터치')
                    trade_executed = True

            elif prev_macd > 0 and current_macd <= 0:  # 데드크로스
                app.logger.info(f"🔍 {ticker} MACD 데드크로스! ({touch_msg})")
                if is_touching:
                    log_trade(app, ticker, 'SELL', current_price, 1, 'MACD음전 + 일목터치')
                    trade_executed = True

            # 매매가 체결되지 않은 경우 현황 보고 전송
            if not trade_executed:
                send_status_report(app, ticker, current_price, current_macd, prev_macd, signal_value, is_touching, "조건 불만족")

            market_state[ticker]['prev_macd'] = current_macd
            return jsonify({'status': 'success', 'msg': 'Logic executed'}), 200

    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500