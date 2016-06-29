import unittest

import import_app_engine
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed
import endpoints


import sys
sys.path.append("..")
from Guess_a_Number.api import *
from Guess_a_Number.models import User, Game, Score


class GuessANumberApiTestCase(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()  




    def testOne(self):
        self.assertTrue(True)
        
    def test_create_user(self):
        container = USER_REQUEST.combined_message_class(
                user_name="lisa",
                email="abc@xyz")        
        api = GuessANumberApi()
        api.create_user(container)
        user = User.query().fetch()[0];
        
        self.assertEqual("lisa", user.name)
        
        
        
if __name__=='__main__':
    unittest.main()  
