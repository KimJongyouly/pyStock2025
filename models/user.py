from flask_login import UserMixin
from datasource.dao import rdb
from werkzeug.security import generate_password_hash

class User(UserMixin):
    def __init__(self, idx, name, email, use_yn, password):
        self.idx = idx
        self.name = name
        self.email = email
        self.use_yn = use_yn
        self.password = password


    def get_id(self):
        return str(self.idx)

    @property
    def is_active(self):
        return self.use_yn == 1

    @staticmethod
    def get(user_id):
        db = rdb()
        db.connect()
        rs = db.query(f"SELECT * FROM users WHERE idx = {user_id}")
        if rs.data:
            user_data = rs.data[0]
            return User(idx=user_data['idx'], name=user_data['name'],
                        email=user_data['email'], use_yn=user_data['use_yn'],
                        password=user_data['password'])
        return None

    @staticmethod
    def get_by_email(email):
        db = rdb()
        db.connect()
        rs = db.query(f"SELECT * FROM users WHERE email = '{email}'")
        if rs.data:
            user_data = rs.data[0]
            return User(idx=user_data['idx'], name=user_data['name'],
                        email=user_data['email'],use_yn=user_data['use_yn'],
                        password=user_data['password'])
        return None

    @staticmethod
    def create(payload):
        db = rdb()
        db.connect()

        if User.get_by_email(payload['email']):
            return {"success": 0, "error_no": "user.error.2", "message": "이미 사용중인 Email 입니다."}

        hashed_password = generate_password_hash(payload['password'])
        rs = db.insert(f"""INSERT INTO users (name, email, password, use_yn) 
                                    VALUES ('{payload['name']}', '{payload['email']}', '{hashed_password}', 0)""")

        if rs.affected == 0:
            return {"success": 0, "error_no": "user.error.3", "message": "유저 등록에 실패했습니다."}

        return {"success": 1, "error_no": "user.error.0", "message": "회원가입 요청이 완료되었습니다."}
