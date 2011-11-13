import unittest
from resources.lib.auth import Auth

class Test(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.auth = Auth()
        
    def test_construct_postData(self):
        expected_data = 'returnOnError=true&userType=REGISTERED_FAN&username=test_user&password=test_pass&returnUrl=http%3A%2F%2Fwww.nhl.com%2Fice%2Fgamecenterlive.htm%3Fid%3D2011020240'
        actual_data = self.auth.construct_postData()
        self.assertEqual(actual_data, expected_data)

#    def test_login(self):
#        self.auth.login()
#        print self.auth.cookiejar._cookies
#        resp = self.auth.open_page('http://www.nhl.com/ice/gamecenterlive.htm?id=2011020222&navid=sb:gamecenterlive')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_construct_postData']
    unittest.main()