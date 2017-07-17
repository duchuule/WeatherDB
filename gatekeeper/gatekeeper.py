from flask import Flask, abort, make_response, request, url_for
import pymongo
import datetime
from dateutil import parser
import math
import json
import bson


app = Flask(__name__)
client = pymongo.MongoClient() # (host="mongo")


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
    #first check to see if it's epoch time
    if isinstance(time, int ):
        return datetime.datetime.fromtimestamp(time, datetime.timezone.utc)
    else:
        return parser.parse(time).replace(tzinfo=datetime.timezone.utc)


# api to get weatehr data
@app.route('/', methods=['GET'])
def get_data():
    if not request.json or 'id' not in request.json:
        return JSONEncoder().encode({"error": "no cityid specified"})

    db = get_db()
    cityid = request.json["id"]

    #when 'time' is requested, return one data point closest to that time
    if 'time' in request.json:
        time = math.floor(datetime_convert(request.json['time']).timestamp())

        #try to find the time closest before an closest after, then comparing them
        closest_before = db.find({"updated_on": {"$lte": time}, "id":cityid}).sort("updated_on", pymongo.DESCENDING)
        closest_after = db.find({"updated_on": {"$gte": time}, "id":cityid}).sort("updated_on", pymongo.ASCENDING)
        if closest_before.count() == 0: #no time before in database
            return JSONEncoder().encode(closest_after[0])
        elif closest_after.count() == 0: #no time after in database
            return JSONEncoder().encode(closest_before[0])
        else:
            if closest_after[0]["updated_on"] - time < time - closest_after[0]["updated_on"]:
                return JSONEncoder().encode(closest_after[0])
            else:
                return JSONEncoder().encode(closest_before[0])
    else:
        return JSONEncoder().encode({"error": "no time specified"})



@app.errorhandler(404)
def not_found(error):
    return make_response(JSONEncoder().encode({'error': 'not found'}), 404)


@app.errorhandler(400)
def not_found(error):
    return make_response(JSONEncoder().encode({'error': 'bad request'}), 400)


if __name__ == "__main__":
    app.run(port=80)