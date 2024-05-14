from flask_login import UserMixin
import modules.database as db


class User(UserMixin):
    def __init__(self, id, username, password, public_key):
        self.id = id
        self.username = username
        self.password = password
        self.publin_key = public_key
        self.authenticated = False

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.authenticated

    def get_id(self):
        return self.id
