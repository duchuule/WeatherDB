import unittest
import pymongo
import pymongo.errors
from gatekeeper import model


class TestWeather(unittest.TestCase):
    def setUp(self):
        super(TestWeather, self).setUp()
        self._client = pymongo.MongoClient()
        self._client.drop_database('testdb')
        self._db = self._client['testdb']
        self._weather = model.Weather(self._db)

        coll = self._weather.get_db()
        # mock data
        entries = [{"id": 4699066, "updated_on": 1500100000}, {"id": 4699066, "updated_on": 1500200000},
                   {"id": 4699066, "updated_on": 1500300000}, {"id": 4699066, "updated_on": 1500400000},
                   {"id": 4699066, "updated_on": 1500500000}, {"id": 4699066, "updated_on": 1500600000},
                   {"id": 4699066, "updated_on": 1500700000}, {"id": 4699066, "updated_on": 1500800000},
                   {"id": 4699066, "updated_on": 1500900000}]
        coll.insert_many(entries)

    def tearDown(self):
        self._client.drop_database('testdb')

    def test_find_closest_early(self):
        ret = self._weather.find_closest(1400000000, 4699066)
        assert len(ret) == 1
        assert ret[0]["updated_on"] == 1500100000

    def test_find_closest_late(self):
        ret = self._weather.find_closest(1600000000, 4699066)
        assert len(ret) == 1
        assert ret[0]["updated_on"] == 1500900000

    def test_find_closest_middle(self):
        ret = self._weather.find_closest(1500530000, 4699066)
        assert len(ret) == 1
        assert ret[0]["updated_on"] == 1500500000

    def test_find_closest_middle2(self):
        ret = self._weather.find_closest(1500570000, 4699066)
        assert len(ret) == 1
        assert ret[0]["updated_on"] == 1500600000

    def test_find_closest_wrong_city_id(self):
        ret = self._weather.find_closest(1500570000, 123)
        assert len(ret) == 0

    def test_interval_begintime_early_endtime_middle(self):
        ret = self._weather.find_interval(1400000000, 1500570000, 4699066)
        timelist = []
        for entry in ret:
            timelist.append(entry["updated_on"])
        assert len(ret) == 5
        assert timelist == [1500100000, 1500200000, 1500300000, 1500400000, 1500500000]

    def test_interval_begintime_middle_endtime_late(self):
        ret = self._weather.find_interval(1500720000, 1600000000, 4699066)
        timelist = []
        for entry in ret:
            timelist.append(entry["updated_on"])
        assert len(ret) == 2
        assert timelist == [1500800000, 1500900000]

    def test_interval_begintime_early_endtime_late(self):
        ret = self._weather.find_interval(1400000000, 1600000000, 4699066)
        timelist = []
        for entry in ret:
            timelist.append(entry["updated_on"])
        assert len(ret) == 9
        assert timelist == [1500100000, 1500200000, 1500300000, 1500400000, 1500500000, 1500600000,
                            1500700000, 1500800000, 1500900000]

    def test_interval_begintime_greater_than_endtime(self):
        ret = self._weather.find_interval(1500800000, 1500400000, 4699066)
        assert len(ret) == 0

    def test_interval_wrong_city_id(self):
        ret = self._weather.find_interval(1500300000, 1500570000, 123)
        assert len(ret) == 0


if __name__ == '__main__':
    unittest.main()
