import FinanceDataReader as fdr
import plotly.graph_objects as go
from flask import jsonify
from plotly.subplots import make_subplots
import json
import plotly
from datetime import datetime
import numpy as np
from dateutil.relativedelta import relativedelta
from datasource.dao import rdb
import duckdb
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pykrx')

from pykrx import stock


df_krx_cache = None


def get_stock_data(ticker, start=None, end=None, interval='D'):
    global df_krx_cache

    db_sqlite = rdb()
    db_sqlite.connect()

    rs = db_sqlite.query(f"select corp_name from company where stock_code = '{ticker}'")

    if not rs.data:
        return None, None

    if rs.data:  # 데이터가 잇을때만 처리하자
        corp_name = rs.data[0]['corp_name']


    start = (datetime.now() - relativedelta(years=1)).strftime("%Y-%m-%d") if start is None else start
    data_start = '2022-01-01' if start is None else (datetime.strptime(start, "%Y-%m-%d") - relativedelta(years=1)).strftime("%Y-%m-%d")
    end = datetime.now().strftime('%Y-%m-%d') if end is None else end

    # 일단 일봉
    df = fdr.DataReader(ticker, data_start, end)

    # 최근 52주 기준임.
    recent_year = df.iloc[-250:]
    high_52w = recent_year['High'].max()
    low_52w = recent_year['Low'].min()

    if df_krx_cache is None:
        df_krx_cache = fdr.StockListing('KRX')


    duck_sql = f"""
                select * 
                from ( 
                    select 
                    Market, Code, Name, Marcap, 
                    row_number() over ( PARTITION by  Market order by Marcap desc) as rn 
                    from df_krx_cache
                )  
                where Code = '{ticker}'
                """
    df_rank = duckdb.sql(duck_sql).pl()

    if len(df_rank) > 0:
        stock_rank = df_rank.to_pandas()['rn'].tolist()[0]
    else:
        stock_rank = '-'


    df_krx = df_krx_cache
    stock_data_rows = df_krx[df_krx['Code'] == ticker]

    if stock_data_rows.empty:
        return None, None
        
    stock_data = stock_data_rows.iloc[0]
    m_cap_val = stock_data.get('Marcap', stock_data.get('MarketCap', 0))

    """
    지수에서 이정도는 봐야 함. 
        * eps : 올해 얼마 벌었니? (수익성지표) => PER과 관련 
        * bps : 가진 재산 얼마? (안정성 지표)  => PBR과 관련 

    
    Formular 
        * EPS = 당기순이익/발행주식수
        * BPS = 순자산(=자기자본)/발행주식수 ... 
               자기자본 = 자산 - 부채
        ** 발행주식수는 KRX의 데이터 해결 
        ** 당기순이익을 구하려면 Dart.재무정보 -> 배당정보를 봐야 함.
                                          결산월을 이용 전분기의 데이터를 가져와서 보통 계산함. 
                                          매일의 발행주식이 다를 수 있으므로 매일 eps를 구하기도 함. 
    ==> 우린 전문가모드가 아니므로 또는 그렇게 하면 일이 열라게 커지므로... 
        pykrx를 이용하자... 
    
    """
    yesterday = (datetime.now() - relativedelta(days=1)).strftime('%Y-%m-%d')
    df_index = stock.get_market_fundamental(yesterday, yesterday, ticker)
    if df_index.empty:
        per = 0
        pbr = 0
    else:
        stock_index = df_index.iloc[0]
        per = stock_index.get('PER', 0)
        pbr = stock_index.get('PBR', 0)


    info = {
        'corp_name': corp_name,
        'market_cap': int(m_cap_val / 100000000) if m_cap_val else 0,  # 억 단위 변환
        'stock_issue': "{:,.0f}".format(stock_data.get('Stocks', 0)),
        'stock_rank': stock_rank,
        'high_52w': high_52w,
        'low_52w': low_52w,
        'per': per,
        'pbr': pbr
    }


    # 주봉 월봉
    if interval.upper() == 'W':  # 월요일 시작
        df = df.resample('W-MON').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        })
    elif interval.upper() == 'M':  # ME는 Month End
        df = df.resample('ME').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        })

    # 이평
    df['MA5'] = df['Close'].rolling(window=5, min_periods=1).mean()
    df['MA10'] = df['Close'].rolling(window=10, min_periods=1).mean()
    ma_window = 280 if interval.upper() == 'D' else 60
    df['MA54W'] = df['Close'].rolling(window=ma_window, min_periods=1).mean()

    # 골든/데드 크로스
    # 주가가 54주선을 상향 돌파하면 골든크로스, 하향 돌파하면 데드크로스
    df['Prev_Close'] = df['Close'].shift(1)
    df['Prev_MA54W'] = df['MA54W'].shift(1)

    # Trace : Linear Regression
    y = df['Close'].values
    x = np.arange(len(y))
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    df['Trend'] = p(x)

    df_plot = df.loc[start:].copy()
    vol_colors = ['red' if row['Close'] >= row['Open'] else 'blue' for _, row in df_plot.iterrows()]
    df_plot['Prev_Close'] = df_plot['Close'].shift(1)
    df_plot['Prev_MA54W'] = df_plot['MA54W'].shift(1)
    golden_mask = (df_plot['Prev_Close'] < df_plot['Prev_MA54W']) & (df_plot['Close'] > df_plot['MA54W'])
    dead_mask = (df_plot['Prev_Close'] > df_plot['Prev_MA54W']) & (df_plot['Close'] < df_plot['MA54W'])
    gold_points = df_plot[golden_mask]
    dead_points = df_plot[dead_mask]

    # 서브플롯 생성
    fig = make_subplots(rows=2,
                        cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_heights=[0.7, 0.3])

    # 캔들차트 추가
    fig.add_trace(go.Candlestick(x=df_plot.index,
                                 open=df_plot['Open'],
                                 high=df_plot['High'],
                                 low=df_plot['Low'],
                                 close=df_plot['Close'],
                                 name=corp_name,
                                 increasing_line_color='red',
                                 decreasing_line_color='blue'),
                  row=1, col=1)

    # 5. 이동평균선들 추가
    # 5일 평균 (주황색)
    fig.add_trace(go.Scatter(x=df_plot.index,
                             y=df_plot['MA5'],
                             line=dict(color='orange', width=1),
                             name='5일 평균'), row=1, col=1)

    # 10일 평균 (초록색)
    fig.add_trace(go.Scatter(x=df_plot.index,
                             y=df_plot['MA10'],
                             line=dict(color='green', width=1),
                             name='10일 평균'), row=1, col=1)

    # 52주 평균 (보라색, 굵게)
    fig.add_trace(go.Scatter(x=df_plot.index,
                             y=df_plot['MA54W'],
                             line=dict(color='purple', width=2),
                             name='54주 평균(MA54W)'), row=1, col=1)

    # 6. 추세선 추가
    fig.add_trace(go.Scatter(x=df_plot.index,
                             y=df_plot['Trend'],
                             line=dict(color='gray', width=2, dash='dash'),
                             name='추세선'), row=1, col=1)

    # 7. 거래량 차트 추가
    fig.add_trace(go.Bar(x=df_plot.index,
                         y=df_plot['Volume'],
                         name='거래량',
                         marker_color=vol_colors,
                         opacity=1.0), row=2, col=1)

    # 8. 골든크로스 표식 (빨간색 위쪽 화살표)
    fig.add_trace(go.Scatter(x=gold_points.index,
                             y=gold_points['Low'] * 0.97,
                             mode='markers',
                             name='Golden',
                             marker=dict(symbol='triangle-up', size=12, color='red')), row=1, col=1)

    # 9. 데드크로스 표식 (파란색 아래쪽 화살표)
    fig.add_trace(go.Scatter(x=dead_points.index,
                             y=dead_points['High'] * 1.03,
                             mode='markers',
                             name='Dead',
                             marker=dict(symbol='triangle-down', size=12, color='blue')), row=1, col=1)

    # 8. 레이아웃 설정
    fig.update_layout(
        # title=f'{corp_name}({ticker})',
        yaxis_title='가격',
        yaxis2_title='거래량',
        xaxis_rangeslider_visible=False,
        height=550,
        template='plotly_white',
        bargap=0.01

    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON, info



def handle_search_stocker(term):
    """
    stock_index.html에서 검색창의 구현부분
    """
    db = rdb()
    db.connect()

    sql = f"""SELECT corp_name, stock_code
         FROM company
         WHERE (corp_name LIKE '%{term}%'
                or stock_code LIKE '%{term}%' )
         and stock_code is not null
         LIMIT 10   """

    results = db.query(sql)

    if results.result and results.data:
        return jsonify([{'name': row['corp_name'], 'code': row['stock_code']} for row in results.data])
    else:
        return jsonify([])


def my_stock_concern(user_id, ticker):
    db_sqlite = rdb()
    db_sqlite.connect()

    # Check if the stock is already in the user's concern list
    check_sql = f"SELECT * FROM my_stock WHERE user_idx = {user_id} AND stock_cd = '{ticker}'"
    existing = db_sqlite.query(check_sql)

    if existing.data:
        # If it exists, remove it
        delete_sql = f"DELETE FROM my_stock WHERE user_idx = {user_id} AND stock_cd = '{ticker}'"
        db_sqlite.delete(delete_sql)
        return {'message': '관심종목에서 해제되었습니다.', 'is_concerned': False}
    else:
        # If it does not exist, add it
        insert_sql = f"INSERT INTO my_stock (user_idx, stock_cd) VALUES ({user_id}, '{ticker}')"
        db_sqlite.insert(insert_sql)
        return {'message': '관심종목으로 등록되었습니다.', 'is_concerned': True}


def is_concern_stock(user_id, ticker):
    db_sqlite = rdb()
    db_sqlite.connect()
    check_sql = f"SELECT * FROM my_stock WHERE user_idx = {user_id} AND stock_cd = '{ticker}'"
    existing = db_sqlite.query(check_sql)
    return bool(existing.data)