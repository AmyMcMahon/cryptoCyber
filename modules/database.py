import sqlite3
from Crypto.Hash import SHA256
import Crypto.Random
from modules.user import User


class Database:
    def __init__(self):
        self.connect = sqlite3.connect("database.db", check_same_thread=False)
        self.connect.execute(
            "CREATE TABLE IF NOT EXISTS USERS (username TEXT, password TEXT, salt TEXT, public_key TEXT, id INTEGER PRIMARY KEY AUTOINCREMENT)"
        )
        self.connect.execute(
            "CREATE TABLE IF NOT EXISTS FILES (sender TEXT, receiver TEXT, file_path TEXT, id INTEGER PRIMARY KEY AUTOINCREMENT, symmetric_key TEXT, iv TEXT)"
        )
        self.cursor = self.connect.cursor()

    def createUser(self, username, password, public_key):
        self.cursor.execute(
            'SELECT public_key FROM USERS WHERE username = "' + username + '"'
        )
        row = self.cursor.fetchone()
        if row is None:
            h = SHA256.new()
            salt = Crypto.Random.get_random_bytes(16)
            saltedPassword = password.encode("utf-8") + salt
            h.update(saltedPassword)
            password = h.hexdigest().encode("utf-8")
            self.cursor.execute(
                "INSERT INTO USERS(username, password, public_key) VALUES (?, ?, ?)",
                (username, password, public_key),
            )
            self.connect.commit()
        else:
            raise Exception("User already exists")

    def getPublicKey(self, username):
        self.cursor.execute(
            'SELECT public_key FROM USERS WHERE username = "' + username + '"'
        )
        row = self.cursor.fetchone()
        return row[0]

    def getPassword(self, username):
        self.cursor.execute(
            "SELECT password, salt FROM USERS WHERE username = ?", (username,)
        )
        row = self.cursor.fetchone()
        if row is None:
            return None
        return row[0], row[1]

    def check_Login(self, username, password):
        pass_hash, salt = self.getPassword(username)
        if pass_hash is None:
            return False

        h = SHA256.new()
        saltedPassword = password.encode("utf-8") + salt
        h.update(saltedPassword)
        passwordLogin = h.hexdigest().encode("utf-8")
        if pass_hash == passwordLogin:
            return True
        else:
            return False

    def getUserId(self, id):
        self.cursor.execute("SELECT * FROM USERS WHERE id = ?", (id,))
        row = self.cursor.fetchone()
        if row is not None:
            return User(int(row[4]), row[0], row[1], row[2])
        else:
            return None

    def getUser(self, username):
        self.cursor.execute('SELECT * FROM USERS WHERE username = "' + username + '"')
        row = self.cursor.fetchone()
        if row is not None:
            return User(int(row[4]), row[0], row[1], row[2])
        else:
            return None

    def insertFile(self, sender, receiver, file_path, symmetric_key, iv):
        self.cursor.execute(
            "INSERT INTO FILES(sender, receiver, file_path, symmetric_key, iv) VALUES (?, ?, ?, ?, ?)",
            (sender, receiver, file_path, symmetric_key, iv),
        )
        self.connect.commit()

    # for debug, get rid of ltr
    def getAllUsersAdmin(self):
        self.cursor.execute("SELECT username, password, public_key FROM USERS")
        rows = self.cursor.fetchall()
        return rows

    def getAllUsers(self):
        self.cursor.execute("SELECT username FROM USERS")
        rows = self.cursor.fetchall()
        return rows

    def getUsersFiles(self, username):
        self.cursor.execute(
            'SELECT sender, file_path FROM FILES WHERE receiver = "' + username + '"'
        )
        rows = self.cursor.fetchall()
        clean_rows = []
        for sender, file_path in rows:
            file_path = file_path.split("/")[-1]
            clean_rows.append((sender, file_path))
        return clean_rows

    def getSymmetricKey(self, file_path):
        self.cursor.execute(
            'SELECT symmetric_key FROM FILES WHERE file_path = "' + file_path + '"'
        )
        row = self.cursor.fetchone()
        return row[0]

    def getIv(self, file_path):
        self.cursor.execute(
            'SELECT iv FROM FILES WHERE file_path = "' + file_path + '"'
        )
        row = self.cursor.fetchone()
        return row[0]

    # maybe get rid of this ltr
    def getAllFilesAdmin(self):
        self.cursor.execute("SELECT sender, receiver, file_path FROM FILES")
        rows = self.cursor.fetchall()
        clean_rows = []
        for sender, receiver, file_path in rows:
            file_path = file_path.split("/")[-1]
            clean_rows.append((sender, receiver, file_path))
        return clean_rows
