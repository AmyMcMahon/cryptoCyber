import unittest
from modules.database import Database


class TestDatebase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        print("Setting up")
        self.db = Database()
        self.db.createUser("testsender", "testpassword", "testpublickey")
        self.db.createUser("testreceicer", "testpassword", "testpublickey")
        self.db.insertFile("testsender", "testreceiver", "testfile", "testsymmetrickey", "testiv")

    def testCheckUserTable(self):
        user1 = "testsender"
        user2 = "testreceicer"
        db1 = self.db.getAllUsersAdmin()[-2:][0]
        db2 = self.db.getAllUsersAdmin()[-2:][1]
        print(db1, db2)
        self.assertEqual(db1[0], user1)
        self.assertEqual(db2[0], user2)

    def testCheckFileTable(self):
        self.assertEqual(
            self.db.getAllFilesAdmin()[-1], ("testsender", "testreceiver", "testfile")
        )

    def testCheckFileForUser(self):
        self.assertEqual(
            self.db.getUsersFiles("testreceiver")[-1], ("testsender", "testfile")
        )

    @classmethod
    def tearDownClass(self):
        print("Tearing down")
        self.db.cursor.execute("DELETE FROM USERS WHERE username = 'testsender'")
        self.db.cursor.execute("DELETE FROM USERS WHERE username = 'testreceiver'")
        self.db.cursor.execute("DELETE FROM FILES WHERE sender = 'testsender'")
        self.db.cursor.execute("DELETE FROM FILES WHERE receiver = 'testreceiver'")
        self.db.connect.commit()


if __name__ == "__main__":
    unittest.main()
