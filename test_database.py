import unittest
import modules.database as Database

class TestDatebase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.db = Database()
        self.db.createUser("testsender", "testpassword", "testpublickey")
        self.db.createUser("testreceicer", "testpassword", "testpublickey")
        self.db.insertFile("testsender", "testreceiver", "testfile")


    def testCheckUserTable(self):
        self.assertEqual(self.db.getAllUsers(),
                         [('testsender', 'testpassword', 'testpublickey'),
                          ('testreceiver', 'testpassword', 'testpublickey')])
        
    def testCheckFileTable(self):
        self.assertEqual(self.db.getAllFilesAdmin(),
                         [('testsender', 'testreceiver', 'testfile')])

    def testCheckFileForUser(self):
        self.assertEqual(self.db.getUsersFiles("testreceiver"),
                         [('testsender', 'testfile')])


if __name__ == '__main__':
    unittest.main()