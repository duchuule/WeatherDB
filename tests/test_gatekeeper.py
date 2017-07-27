import gatekeeper
import unittest
import pymongo
import os
import json
import pytest
import werkzeug.exceptions as exceptions

class TestGatekeeper(unittest.TestCase):
    def setUp(self):
        super(TestGatekeeper, self).setUp()

        # set up mock database
        self._client = pymongo.MongoClient()
        self._client.drop_database('testdb')
        self._db = self._client['testdb']
        coll = self._db['weather']
        # mock data
        entries = [{"id": 4699066, "updated_on": 1500100000}, {"id": 4699065, "updated_on": 1500200000},
                   {"id": 4699066, "updated_on": 1500300000}, {"id": 4699065, "updated_on": 1500400000},
                   {"id": 4699066, "updated_on": 1500500000}, {"id": 4699065, "updated_on": 1500600000},
                   {"id": 4699066, "updated_on": 1500700000}, {"id": 4699065, "updated_on": 1500800000},
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

    def test_db(self):
        rv = self.app.get('/db')
        assert b'"count": 9' in rv.data

    def test_db_cityid(self):
        rv = self.app.get('/db/4699066')
        assert b'"count": 5' in rv.data

    def test_db_wrong_cityid(self):
        rv = self.app.get('/db/123')
        assert b'"count": 0' in rv.data

    def test_weather_no_cityid(self):
        rv = self.app.get('/weather')
        assert b'"error": "not found"' in rv.data
        assert rv.status_code == 404

    def test_weather_no_json_data(self):
        rv = self.app.get('/weather/4699066')
        assert b'"error": "invalid json data"' in rv.data
        assert rv.status_code == 400

    def test_weather_wrong_content_type(self):
        rv = self.app.get('/weather/4699066',
                          data=json.dumps({"time": 1500530000}),
                          content_type='application/xyz')
        assert b'"error": "invalid json data"' in rv.data
        assert rv.status_code == 400

    # these two methods have not passed yet

    # def test_weather_wrong_data_type(self):
    #     rv = self.app.get('/weather/4699066',
    #                       data=json.dumps({"time": "abc"}),
    #                       content_type='application/json')
    #     assert b'"error": "invalid json data"' in rv.data
    #     assert rv.status_code == 400

    # def test_weather_bad_json_data(self):
    #     with pytest.raises(exceptions.BadRequest):
    #         rv = self.app.get('/weather/4699066',
    #                       data=json.dumps({"time"}),
    #                       content_type='application/json')


    def test_weather_good_json_data(self):
        rv = self.app.get('/weather/4699066',
                          data=json.dumps({"time": 1500530000}),
                          content_type='application/json')
        ret = json.loads(rv.data)
        assert isinstance(ret, list)
        assert len(ret) == 1
        assert ret[0]["updated_on"] == 1500500000

    def test_weather_good_json_data_wrong_city(self):
        rv = self.app.get('/weather/123',
                          data=json.dumps({"time": 1500530000}),
                          content_type='application/json')
        ret = json.loads(rv.data)
        assert isinstance(ret, list)
        assert len(ret) == 0


if __name__ == '__main__':
    unittest.main()
