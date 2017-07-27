import pymongo
import datetime
from dateutil import parser
import json
import bson
import math


class DatetimeHelper:
    """helper class for datetime manipulation"""

    @staticmethod
    def to_datetime(time):
        if isinstance(time, datetime.datetime):  # first, check to see if it's already datetime
            return time
        if isinstance(time, int):  # second check to see if it's epoch time
            return datetime.datetime.fromtimestamp(time, datetime.timezone.utc)
        else:
            try:
                return parser.parse(time).replace(tzinfo=datetime.timezone.utc)
            except ValueError:
                raise ValueError('time string needs to follow ISO 8601 format')


class JSONEncoder(json.JSONEncoder):
    """helper class for json encode because jsonify does not work with mongo data"""

    def default(self, o):
        if isinstance(o, bson.ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class Weather:
    """Class to query database and return requested entries"""

    def __init__(self, database):
        self._db = database
        self._coll = self._db["weather"]

    def get_db(self):
        return self._coll

    def get_count(self, payload, city_id):
        # when 'time' is requested, return one data point closest to that time
        if 'time' in payload:
            try:
                time = math.floor(DatetimeHelper.to_datetime(payload['time']).timestamp())
            except ValueError as e:
                return {"status": "error", "code": 400, "message": str(e)}

            return {"status": "success", "result": self.find_closest(time, city_id)}

        # when users request data for an a time interval
        elif 'begintime' in payload and 'endtime' in payload:
            try:
                begintime = math.floor(DatetimeHelper.to_datetime(payload['begintime']).timestamp())
                endtime = math.floor(DatetimeHelper.to_datetime(payload['endtime']).timestamp())
            except ValueError as e:
                return {"status": "error", "code": 400, "message": str(e)}

            return {"status": "success", "result": self.find_interval(begintime, endtime, city_id)}
        else:
            return {"status": "error", "message": "no time specified", "code": 400}

    def find_closest(self, time, cityid):
        """ find weather record for a city at time closest to the specified time"""

        # try to find the a time closest before and a time closest after, then comparing them
        closest_before = self._coll.find({"updated_on": {"$lte": time}, "id": cityid}).sort("updated_on",
                                                                                            pymongo.DESCENDING)
        closest_after = self._coll.find({"updated_on": {"$gte": time}, "id": cityid}).sort("updated_on",
                                                                                           pymongo.ASCENDING)
        if closest_before.count() == 0 and closest_after.count() == 0:
            return []
        elif closest_before.count() == 0 and closest_after.count() > 0:  # no time before in database
            return [closest_after[0]]
        elif closest_after.count() == 0 and closest_before.count() > 0:  # no time after in database
            return [closest_before[0]]
        else:
            if closest_after[0]["updated_on"] - time < time - closest_before[0]["updated_on"]:
                return [closest_after[0]]
            else:
                return [closest_before[0]]

    def find_interval(self, begintime, endtime, cityid):
        """ find all weather records for a city that happened in a time interval"""

        entries = self._coll.find({"updated_on": {"$gte": begintime, "$lte": endtime}, "id": cityid}) \
            .sort("updated_on", pymongo.ASCENDING)
        entries_list = []
        for entry in entries:
            entries_list.append(entry)
        return entries_list
