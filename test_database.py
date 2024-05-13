import unittest
from modules.database import Database

class TestDatebase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        print("Setting up")
        self.db = Database()
        self.db.createUser("testsender", "testpassword", "testpublickey")
        self.db.createUser("testreceicer", "testpassword", "testpublickey")
        self.db.insertFile("testsender", "testreceiver", "testfile")


    def testCheckUserTable(self):
        self.assertEqual(self.db.getAllUsersAdmin()[-2:],
                         [('testsender', 'testpassword', 'testpublickey'), ('testreceicer', 'testpassword', 'testpublickey')])
        
    def testCheckFileTable(self):
        self.assertEqual(self.db.getAllFilesAdmin()[-1],
                         ('testsender', 'testreceiver', 'testfile'))

    def testCheckFileForUser(self):
        self.assertEqual(self.db.getUsersFiles("testreceiver")[-1],
                         ('testsender','testfile'))


if __name__ == '__main__':
    unittest.main()