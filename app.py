from flask import Flask, request, flash, redirect, url_for, render_template, make_response, jsonify
import click
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from utils.mylogs import setup_logging
from utils.notify import ctelegram
from datasource.dao import rdb, init_corp
from configure.config import conf
from collections import defaultdict
from controllers.webhook import handle_webhook
from models.user import User
from models.stocker import get_stock_data, handle_search_stocker, my_stock_concern, is_concern_stock
from models.forecaster import LSTMForecaster
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta



app = Flask(__name__)
app.secret_key = "sugar-rain-stoking"
setup_logging(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.unauthorized_handler
def unauthorized():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(error='Unauthorized'), 401
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.get(int(user_id))
    except (ValueError, TypeError):
        return None

# # telegram
# obj_telegram = ctelegram()

market_state = defaultdict(dict)


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    return handle_webhook(app, market_state, data)


@app.route('/')
def index():
    """
    로그인/회원가입 페이지 렌더링
    """
    return render_template('login.html')


@app.route('/signup', methods=('POST',))
def signup():
    """
    회원가입 처리
    """
    payload = {"name": request.form.get('name'),
               "email": request.form.get('email'),
               "password": request.form.get('password')}

    if not all(payload.values()):
        flash("모든 필드를 입력해주세요.", 'error')
        return redirect(url_for('index'))

    result = User.create(payload)
    flash(f"{result['message']}", 'success' if result['success'] > 0 else 'error')

    return redirect(url_for('index'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 처리"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.get_by_email(email)

        if not user:
            flash('등록되지 않은 이메일입니다.', 'error')
            return redirect(url_for('login'))

        if not check_password_hash(user.password, password):
            flash('email, 비밀번호가 일치 하지 않습니다.', 'error')
            return redirect(url_for('login'))

        if not user.is_active:
            flash('관리자 승인을 받기 전입니다.', 'error')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('stock_index'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/stock_index')
@login_required
def stock_index():
    ticker = request.args.get('ticker')
    if not ticker:
        user_id = int(current_user.get_id())
        db_sqlite = rdb()
        db_sqlite.connect()
        sql = f"SELECT stock_cd FROM my_stock WHERE user_idx = {user_id} ORDER BY id DESC LIMIT 1"
        result = db_sqlite.query(sql)
        if result.data:
            ticker = result.data[0]['stock_cd']
        else:
            ticker = '005930'  # Default if no ticker in args and no stock in my_stock

    start = request.args.get('start')
    if not start or start == 'None':start = None
    end =  request.args.get('end')
    if not end or end == 'None': end = None

    interval = request.args.get('interval', 'D')
    graphJSON, info = get_stock_data(ticker, start=start, end=end, interval=interval)

    if graphJSON is None:
        flash('주식 코드 확인 !!', 'error')
        return redirect(url_for('stock_index'))


    return render_template('stock_index.html',
                           graphJSON=graphJSON,
                           info=info,
                           ticker=ticker,
                           start=start,
                           end=end)



@app.route('/search')
@login_required
def search():
    """
    검색하기 2자이상일때
    """
    term = request.args.get('term', '').strip()
    if not term or len(term) < 2:
        return jsonify([])

    return handle_search_stocker(term)


@app.route('/my_stock_concern/<ticker>')
@login_required
def my_stock_concern_route(ticker):
    """
    관심주 토글하기
    """
    user_id = int(current_user.get_id())
    if request.args.get('check'):
        return jsonify({'is_concerned': is_concern_stock(user_id, ticker)})
    else:
        result = my_stock_concern(user_id, ticker)
        return jsonify(result)



@app.route('/forecast/<ticker>')
@login_required
def forecaster(ticker):
    """
    Endpoint to get stock forecast data.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3 * 365)
    df = fdr.DataReader(ticker, start_date, end_date)

    if df.empty:
        return {'error': 'Could not fetch stock data.'}

    close_prices = df['Close'].values

    forecaster_model = LSTMForecaster(n_steps=60)
    forecaster_model.build_and_train(close_prices, epochs=20)

    predicted_prices = forecaster_model.predict(days_to_predict=30)

    last_date = df.index[-1]
    future_dates = [last_date + timedelta(days=i) for i in range(1, 31)]
    future_dates_str = [d.strftime('%Y-%m-%d') for d in future_dates]

    forecast_data = {
        'dates': future_dates_str,
        'prices': predicted_prices
    }

    return jsonify(forecast_data)



@app.cli.command("init-db")
def init_db_command():
    """
    Clear existing data and create new tables.
    """
    db_sqlite = rdb()
    db_sqlite.connect()
    db_sqlite.init_db()
    init_corp()
    click.echo("Initialized the database and loaded company data.")


if __name__ == '__main__':
    app.run(host=conf.FLASK_HOST,
            port=int(conf.FLASK_PORT),
            debug=conf.FLASK_DEBUG.lower() == 'true',
            use_reloader=True)  ## 파일수정되면 자동 reload

