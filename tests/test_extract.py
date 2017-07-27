import unittest
import pymongo
import pymongo.errors
from extractor import extract, config
from extractor import app


class TestExtractor(unittest.TestCase):
    def setUp(self):
        super(TestExtractor, self).setUp()

        # initialize mock database and extractor object
        app.config.from_object(config)
        self._client = pymongo.MongoClient()
        self._client.drop_database('testdb')
        self._db = self._client['testdb']
        self._extractor = extract.Extractor(app.config["CITIES"], self._db, app.config["API_KEY"])

    def tearDown(self):
        self._client.drop_database('testdb')

    def test_empty_db(self):
        ret = self._extractor.get_db().find().count()
        assert ret == 0

    def test_get_weather(self):
        self._extractor.get_weather()
        ret = self._extractor.get_db().find().count()
        assert ret == 5


if __name__ == '__main__':
    unittest.main()
