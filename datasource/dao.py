import sqlite3
from collections import namedtuple
from configure.config import conf, ROOT_DIR
import os
import sys
import pandas as pd

class qry:
    """
    dao의 method..
    inherit을 위해 정의
    """
    def __init__(self):
        """
        result data
        """
        self.result = namedtuple("rs", ['data', 'result', 'affected', 'lastrowid', 'sql'])
        self.rs = dict()

    def query(self, sql):
        """
        select
        """
        rs = None
        try:
            self.cursor.execute(sql)
            trs = self.cursor.fetchall()

            self.rs = {'data': [{k: r[k] for k in r.keys()} for r in trs],
                       'result': 1,
                       'affected': self.cursor.rowcount,
                       'lastrowid': None,
                       'sql': sql}

        except Exception as e:
            raise Exception(e)
            self.rs = {'data': None,
                       'result': 0,
                       'affected': None,
                       'lastrowid': None,
                       'sql': sql
                       }
        finally:
            return self.result(**self.rs)

    def insert(self, sql):
        """
        insert
        """
        try:
            self.cursor.execute(sql)
            self.rs = {'data': None,
                       'result': 1,
                       'affected': self.cursor.rowcount,
                       'lastrowid': self.cursor.lastrowid,
                       'sql': sql}
        except Exception as e:
            raise Exception(e)
            self.rs = {'data': None,
                       'result': 0,
                       'affected': None,
                       'lastrowid': -1,
                       'sql': sql}
        finally:
            return self.result(**self.rs)

    def delete(self, sql):
        """
        delete
        """
        try:
            self.cursor.execute(sql)
            self.rs = {'data': None,
                       'result': 1,
                       'affected': self.cursor.rowcount,
                       'lastrowid': self.cursor.lastrowid,
                       'sql': sql}
        except Exception as e:
            raise Exception(e)
            self.rs = {'data': None,
                       'result': 0,
                       'affected': None,
                       'lastrowid': -1,
                       'sql': sql}
        finally:
            return self.result(**self.rs)

    def update(self, sql):
        """
        update
        """
        try:
            self.cursor.execute(sql)
            self.rs = {'data': None,
                       'result': 1,
                       'affected': self.cursor.rowcount,
                       'lastrowid': self.cursor.lastrowid,
                       'sql': sql}
        except Exception as e:
            raise Exception(e)
            self.rs = {'data': None,
                       'result': 0,
                       'affected': None,
                       'lastrowid': -1,
                       'sql': sql}
        finally:
            return self.result(**self.rs)

    def command(self, sql):
        """
        ddl, etc...
        """
        try:
            self.cursor.execute(sql)
            self.rs = {'data': None,
                       'result': 1,
                       'affected': 0,
                       'lastrowid': 0,
                       'sql': sql}
        except Exception as e:
            raise Exception(e)
            self.rs = {'data': None,
                       'result': 0,
                       'affected': None,
                       'lastrowid': -1,
                       'sql': sql}
        finally:
            return self.result(**self.rs)


    def init_db(self):
        """
        initalize database
        my_stock.stock_type ==> 1관심가주, 2투자했주, 3관심꺼주, 4모의했주

        """
        sql = {"my_stock": """
                                CREATE TABLE IF NOT EXISTS my_stock (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    user_idx integer, 
                                    stock_cd varchar(15) not null, 
                                    stock_type tinyint,  
                                    created_at DATETIME DEFAULT (DATETIME('now', 'localtime')) 
                                ); 
                            """,
                "trades": """
                                CREATE TABLE IF NOT EXISTS trades (
                                    dt varchar(20), 
                                    user_idx integer,
                                    stock_cd varchar(15), 
                                    ord bigint, 
                                    price bigint, 
                                    quantity int, 
                                    reason   text
                                    );  
                            """,
               "trades.index_1": "CREATE INDEX IF NOT EXISTS idx_trades_dt_cd ON trades (user_idx, dt, stock_cd);",
               "trades.index_2": "CREATE INDEX IF NOT EXISTS idx_trades_cd ON trades (user_idx, stock_cd);",
               "users": """CREATE TABLE IF NOT EXISTS users (
                                    idx INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT NOT NULL,
                                    email TEXT NOT NULL UNIQUE,
                                    password TEXT NOT NULL, 
                                    use_yn tinyint default 0
                                );
               """,
               "company": """create table IF NOT EXISTS company(
                                    corp_code vharchar(20),
                                    corp_name varchar(512),
                                    corp_eng_name varchar(512),
                                    stock_code varchar(20),
                                    modify_date varchar(8)
                                )
                            """,
               "company.index_1": """create unique index IF NOT EXISTS idx_corp_stock on company(corp_code, stock_code);""",
               "company.index_2": """create unique index IF NOT EXISTS idx_stock on company(stock_code);""",
               "company_detail": """create table if not exists company_detail ( 
                                    corp_code varchar(20), 
                                    corp_name varchar(512), 
                                    corp_eng_name varchar(512), 
                                    stock_name varchar(512), 
                                    stock_code varchar(20), 
                                    ceo_nm varchar(512), 
                                    corp_cls varchar(5), 
                                    jurir_no varchar(20), 
                                    bizr_no varchar(20), 
                                    adres varchar(512), 
                                    hm_url varchar(512), 
                                    ir_url varchar(512), 
                                    phn_no varchar(50), 
                                    fax_no varchar(50), 
                                    fax_no varchar(50), 
                                    induty_code varchar(10), 
                                    est_dt char(8), 
                                    acc_mt varchar(2)
                                )""",
               "company_detail.index_1": """create unique index IF NOT EXISTS idx_corp_stock on company_detail(corp_code, stock_code);""",
               "company_detail.index_2": """create unique index IF NOT EXISTS idx_stock on company_detail(stock_code);""",
               }

        for k, v in sql.items():
            try:
                self.command(v)
            except Exception as e:
                raise Exception(e)



class rdb(qry):
    """
    database connect & query
    """
    def __init__(self, db_file=None):
        """
        db_file=절대경로
        path : LOG_DIR
        conf.SQLITE3 = trades.db
        """
        super().__init__()
        self.cursor = None
        self.host = db_file if db_file is not None else f"{ROOT_DIR}{os.sep}{conf.LOG_DIR}{os.sep}{conf.SQLITE3}"

    def connect(self):
        """
        connection
        """
        try:
            if sys.version_info >= (3, 12):
                self.conn = sqlite3.connect(self.host, isolation_level=None, autocommit=True)
            else:
                self.conn = sqlite3.connect(self.host, isolation_level=None)

            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        except Exception as e:
            raise Exception(e)

    def conn_object(self):
        """
        connection
        """
        try:
            if sys.version_info >= (3, 12):
                self.conn = sqlite3.connect(self.host, isolation_level=None, autocommit=True)
            else:
                self.conn = sqlite3.connect(self.host, isolation_level=None)

            return self.conn
        except Exception as e:
            raise Exception(e)



def init_corp():
    """
    로드해야 할 데이터가 좀되서 분리함.
    from dart 고유코드(company), 기업개황(company_detail)만 가져옴
    참고
        https://opendart.fss.or.kr/guide/main.do?apiGrpCd=DS001
    """
    # company
    db_sqlite = rdb()
    db_sqlite.connect()
    df = pd.read_xml(f'{ROOT_DIR}/datasource/corpCode.xml', xpath='./list')
    db_sqlite.delete("delete from company")
    df.to_sql('company', db_sqlite.conn_object(), if_exists='append', index=False)
    # cleansing
    db_sqlite.update("update company set stock_code = null where trim(stock_code) == '';")
    db_sqlite.update("update company set corp_eng_name = null where trim(corp_eng_name) == '';")
    db_sqlite.update("update company set corp_name = null where trim(corp_name) == '';")

    # # company_detail
    # df = pd.read_excel(f'{ROOT_DIR}/datasource/company_detail.xlsx')
    # db_sqlite.delete("delete from company_detail")
    # df.to_sql('company', db_sqlite.conn_object(), if_exists='append', index=False)
    # # cleansing
    # db_sqlite.update("update company set stock_code = null where trim(stock_code) == '';")
    # db_sqlite.update("update company set corp_eng_name = null where trim(corp_eng_name) == '';")
    # db_sqlite.update("update company set corp_name = null where trim(corp_name) == '';")
