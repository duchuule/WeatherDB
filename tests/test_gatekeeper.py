import gatekeeper
import unittest
import pymongo
import os


class TestGatekeeper(unittest.TestCase):
    def setUp(self):
        super(TestGatekeeper, self).setUp()

        # set up mock database
        self._client = pymongo.MongoClient()
        self._client.drop_database('testdb')
        self._db = self._client['testdb']
        coll = self._db['weather']
        # mock data
        entries = [{"id": 4699066, "updated_on": 1500100000}, {"id": 4699066, "updated_on": 1500200000},
                   {"id": 4699066, "updated_on": 1500300000}, {"id": 4699066, "updated_on": 1500400000},
                   {"id": 4699066, "updated_on": 1500500000}, {"id": 4699066, "updated_on": 1500600000},
                   {"id": 4699066, "updated_on": 1500700000}, {"id": 4699066, "updated_on": 1500800000},
                   {"id": 4699066, "updated_on": 1500900000}]
        coll.insert_many(entries)

        # connect gatekeeper to mock database
        os.environ["DBNAME"] = "testdb"
        gatekeeper.views.connect_db()

        # set up test client
        gatekeeper.app.testing = True
        self.app = gatekeeper.app.test_client()

    def tearDown(self):
        self._client.drop_database('testdb')

    def test_not_found(self):
        rv = self.app.get('/')
        assert b'"error": "not found"' in rv.data
        assert rv.status_code == 404

    def test_db_count(self):
        rv = self.app.get('/db')
        assert b'"count": 9' in rv.data
        assert rv.status_code == 200

if __name__ == '__main__':
    unittest.main()
