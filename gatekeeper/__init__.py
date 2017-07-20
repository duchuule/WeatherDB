from flask import Flask, make_response, request
import pymongo
import datetime
from dateutil import parser
import math
import json
import bson

app = Flask(__name__)
client = pymongo.MongoClient(host="mongo")


# helper function for json encode because jsonify sucks
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bson.ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def get_db():
    coll = client.weatherdb.weather
    return coll


def datetime_convert(time):
    # first check to see if it's epoch time
    if isinstance(time, int):
        return datetime.datetime.fromtimestamp(time, datetime.timezone.utc)
    else:
        return parser.parse(time).replace(tzinfo=datetime.timezone.utc)


# api to get weather data
@app.route('/', methods=['GET'])
def get_data():
    db = get_db()
    try:
        if not request.json:
            return JSONEncoder().encode({"error": "invalid json data"})
    except Exception as e:
        # note: this will happen if json data do not escape the quotes around "count", "time", etc
        return JSONEncoder().encode({"error": "invalid json data", "exception": str(e)})

    # these commands do not require cityid
    if 'count' in request.json:
        if request.json['count'] == 'all':  # requesting sum total number of entries in database
            return JSONEncoder().encode({"count": db.count()})
        else:  # requesting only number of entries for 1 city
            cityid = request.json['count']
            return JSONEncoder().encode(db.find({"id": cityid}).count())

    # the remaining commands require city id, so check for id field
    if 'id' not in request.json:
        return JSONEncoder().encode({"error": "invalid json data"})

    cityid = request.json["id"]

    # when 'time' is requested, return one data point closest to that time
    if 'time' in request.json:
        time = math.floor(datetime_convert(request.json['time']).timestamp())

        # try to find the a time closest before and a time closest after, then comparing them
        closest_before = db.find({"updated_on": {"$lte": time}, "id": cityid}).sort("updated_on", pymongo.DESCENDING)
        closest_after = db.find({"updated_on": {"$gte": time}, "id": cityid}).sort("updated_on", pymongo.ASCENDING)
        if closest_before.count() == 0:  # no time before in database
            return JSONEncoder().encode(closest_after[0])
        elif closest_after.count() == 0:  # no time after in database
            return JSONEncoder().encode(closest_before[0])
        else:
            if closest_after[0]["updated_on"] - time < time - closest_after[0]["updated_on"]:
                return JSONEncoder().encode(closest_after[0])
            else:
                return JSONEncoder().encode(closest_before[0])
    # when users request data for an a time interval
    elif 'begintime' in request.json and 'endtime' in request.json:
        begintime = math.floor(datetime_convert(request.json['begintime']).timestamp())
        endtime = math.floor(datetime_convert(request.json['endtime']).timestamp())
        entries = db.find({"updated_on": {"$gte": begintime, "$lte": endtime}, "id": cityid}) \
            .sort("updated_on", pymongo.ASCENDING)
        entries_list = []
        for entry in entries:
            entries_list.append(entry)
        return JSONEncoder().encode(entries_list)
    else:
        return JSONEncoder().encode({"error": "no time specified"})


@app.errorhandler(404)
def not_found():
    return make_response(JSONEncoder().encode({'error': 'not found'}), 404)


@app.errorhandler(400)
def bad_request():
    return make_response(JSONEncoder().encode({'error': 'bad request'}), 400)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
