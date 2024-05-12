import sqlite3

class Database():
    def __init__(self):
        self.connect = sqlite3.connect("database.db", check_same_thread=False)
        self.connect.execute(
        "CREATE TABLE IF NOT EXISTS USERS (username TEXT, password TEXT, public_key TEXT)"
        )
        self.connect.execute(
            "CREATE TABLE IF NOT EXISTS FILES (sender TEXT, receiver TEXT, file_path TEXT, id INTEGER PRIMARY KEY AUTOINCREMENT)"
        )
        self.cursor = self.connect.cursor()

    def createUser(self, username, password, public_key):

        self.cursor.execute(
            "INSERT INTO USERS(username, password, public_key) VALUES (?, ?, ?)",
            (username, password, public_key),
        )
        self.connect.commit()

    def getPassword(self, username):

        self.cursor.execute('SELECT password FROM USERS WHERE username = "' + username + '"')
        row = self.cursor.fetchone()
        return row[0]
    
    def insertFile(self, sender, receiver, file_path):

        self.cursor.execute(
            "INSERT INTO FILES(sender, receiver, file_path) VALUES (?, ?, ?)",
            (sender, receiver, file_path),
        )
        self.connect.commit()

    #for debug, get rid of ltr
    def getAllUsers(self):
        self.cursor.execute("SELECT username, password,public_key FROM USERS")
        rows = self.cursor.fetchall()
        return rows
    
