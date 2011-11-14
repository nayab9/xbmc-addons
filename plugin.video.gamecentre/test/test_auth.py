import unittest
from resources.lib.auth import Auth

class Test(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.auth = Auth()
        
    def test_get_game_info(self):
        self.auth.login()
        for k,v in self.auth.cookiejar._cookies.iteritems():
            print k
            print v
        print len(self.auth.cookiejar._cookies)
        resp = self.auth.get_game_info(None)
        print resp.headers
        print resp.read()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_construct_postData']
    unittest.main()