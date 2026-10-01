from flask_mysqldb import MySQL  # type: ignore[import-not-found]
from werkzeug.security import check_password_hash

mysql = MySQL()


class User:
    def __init__(self, id, username, password_hash, full_name, role, is_active=True):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.full_name = full_name
        self.role = role
        self._is_active = bool(is_active)

    @property
    def is_active(self):
        return self._is_active

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_id(user_id):
        connection = mysql.connection
        if connection is None:
            raise RuntimeError("MySQL connection is unavailable.")
        cur = connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        cur.close()
        if row:
            return User(row['id'], row['username'], row['password_hash'], row['full_name'], row['role'], row['is_active'])
        return None

    @staticmethod
    def get_by_username(username):
        ...