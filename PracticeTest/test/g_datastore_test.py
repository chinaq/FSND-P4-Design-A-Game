import unittest

import import_app_engine
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

import sys
sys.path.append("..")
from src.g_datastore import *

        
        
class DatastoreTestCase(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()    
    
    
    
    def testInsertEntity(self):
        TestModel().put()
        self.assertEqual(1, len(TestModel.query().fetch(2)))

    def testFilterByNumber(self):
        root = TestEntityGroupRoot(id="root")
        TestModel(parent=root.key).put()
        TestModel(number=17, parent=root.key).put()
        query = TestModel.query(ancestor=root.key).filter(
            TestModel.number == 42)
        results = query.fetch(2)
        self.assertEqual(1, len(results))
        self.assertEqual(42, results[0].number)

        
    def testGetEntityViaMemcache(self):
        entity_key = TestModel(number=18).put().urlsafe()
        retrieved_entity = GetEntityViaMemcache(entity_key)
        self.assertNotEqual(None, retrieved_entity)
        self.assertEqual(18, retrieved_entity.number)
        
        
        
if __name__=='__main__':
    unittest.main()
    