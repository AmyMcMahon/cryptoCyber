import sqlite3
from modules.user import User
import bcrypt


class Database:
    def __init__(self):
        self.connect = sqlite3.connect("database.db", check_same_thread=False)
        self.connect.execute(
            "CREATE TABLE IF NOT EXISTS USERS (username TEXT, password TEXT, public_key TEXT, signKey TEXT, id INTEGER PRIMARY KEY AUTOINCREMENT)"
        )
        self.connect.execute(
            "CREATE TABLE IF NOT EXISTS FILES (sender TEXT, receiver TEXT, file_path TEXT, id INTEGER PRIMARY KEY AUTOINCREMENT, symmetric_key TEXT, signed_file, iv TEXT)"
        )
        self.cursor = self.connect.cursor()

    def createUser(self, username, password, public_key, signingKey):
        self.cursor.execute(
            'SELECT public_key FROM USERS WHERE username = "' + username + '"'
        )
        row = self.cursor.fetchone()
        if row is None:
            salt = bcrypt.gensalt(rounds=16)
            hash_pass = bcrypt.hashpw(password.encode("utf-8"), salt)

            self.cursor.execute(
                "INSERT INTO USERS(username, password, public_key, signKey) VALUES ( ?, ?, ?, ?)",
                (username, hash_pass, public_key, signingKey),
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
            "SELECT password FROM USERS WHERE username = ?", (username,)
        )
        row = self.cursor.fetchone()
        if row is None:
            return None
        return row[0]

    def check_Login(self, username, password):
        try:
            pass_hash = self.getPassword(username)
        except:
            return False
        userPass = password.encode("utf-8")
        result = bcrypt.checkpw(userPass, pass_hash)
        if result:
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

    def insertFile(self, sender, receiver, file_path, symmetric_key, signed_file, iv):
        self.cursor.execute(
            "INSERT INTO FILES(sender, receiver, file_path, symmetric_key, signed_file, iv) VALUES (?, ?, ?, ?, ?, ?)",
            (sender, receiver, file_path, symmetric_key, str(signed_file), iv),
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

    # returns only file path
    def getUsersFiles(self, username):
        self.cursor.execute(
            'SELECT sender, file_path, id FROM FILES WHERE receiver = "'
            + username
            + '"'
        )
        rows = self.cursor.fetchall()
        clean_rows = []
        for sender, file_path, id in rows:
            file_path = file_path.split("/")[-1]
            clean_rows.append((sender, file_path, id))
        return clean_rows

    def getFileKeys(self, id):
        self.cursor.execute(
            'SELECT symmetric_key, iv FROM FILES WHERE id = "' + id + '"'
        )
        row = self.cursor.fetchone()
        return row[0], row[1]

    def getFilePath(self, id):
        self.cursor.execute('SELECT file_path FROM FILES WHERE id = "' + id + '"')
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
