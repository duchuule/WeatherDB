from flask import Flask, jsonify, abort, make_response, request, url_for
import pymongo
import datetime
from dateutil import parser



app = Flask(__name__)
client = pymongo.MongoClient() # (host="mongo")


def get_db():
    coll = client.weatherdb.weather
    return coll

def datetime_convert(time):
    #first check to see if it's epoch time
    if isinstance( time, int ):
        return datetime.datetime.fromtimestamp(time)
    else:
        return parser.parse(time)


# api to get weatehr data
@app.route('/', methods=['GET'])
def get_data():
    if not request.json or 'id' not in request.json:
        abort(400)

    #when 'time' is requested, return one data point closest to that time
    if 'time' in request.json:
        time = datetime_convert(request.json['time'])


    return jsonify({"test": time})



@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'not found'}), 404)


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'bad request'}), 400)


if __name__ == "__main__":
    app.run(port=80)