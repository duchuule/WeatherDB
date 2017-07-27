import os
import unittest
import pymongo
import pymongo.errors
import json
import time

# initialize mock database and set environment variable
client = pymongo.MongoClient()
client.drop_database('testdb')
db = client['testdb']
os.environ["DBNAME"] = "testdb"  # set environment variable before import anything from extractor
import extractor


class TestExtractor(unittest.TestCase):
    def setUp(self):
        # set up test client
        extractor.app.testing = True
        self.app = extractor.app.test_client()

    def tearDown(self):
        pass

    def test_homepage(self):
        rv = self.app.get('/')
        ret = json.loads(rv.data)
        assert "DELAY" in ret
        assert "CITIES" in ret

    def test_not_found(self):
        rv = self.app.get('/xyz')
        assert b'"error": "not found"' in rv.data
        assert rv.status_code == 404

    def test_db(self):
        # time.sleep(10)
        rv = self.app.get('/db')
        ret = json.loads(rv.data)
        assert "count" in ret #count is zero unless we wait for the scheduler to extract data from server

    def test_change_delay(self):
        rv = self.app.put('/config', data='{"delay": 10}', content_type='application/json')
        assert b'"DELAY": 10' in rv.data

if __name__ == '__main__':
    unittest.main()
