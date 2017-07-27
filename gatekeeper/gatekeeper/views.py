from flask import make_response, request, jsonify
from .model import Weather, JSONEncoder
import werkzeug.exceptions as exceptions

import os
import pymongo

from gatekeeper import app

weather = None


def connect_db():
    host = os.getenv('DBHOST', "localhost")  # host name will be set by docker through environment variable if needed
    dbname = os.getenv('DBNAME', 'weatherdb')  # database name will be set by test cases if needed
    db = pymongo.MongoClient(host)[dbname]
    global weather
    weather = Weather(db)


# connect to database
connect_db()


@app.route('/db', methods=['GET'])
def get_db_info():
    """api to get general database info"""
    db = weather.get_db()
    return jsonify({"count": db.count()})


@app.route('/db/<int:city_id>', methods=['GET'])
def get_db_city_info(city_id):
    """api to get database info for 1 particulr city"""
    db = weather.get_db()
    return jsonify({"count": db.find({"id": city_id}).count()})


@app.route('/weather/<int:city_id>', methods=['GET'])
def get_weather(city_id):
    """api to get weather data for a particular city"""
    try:
        payload = request.get_json()
    # BadRequest exception will be raised if json data is not formated properly
    # and decoding of json data failed.
    except exceptions.BadRequest as e:
        return make_response(jsonify({"error": "bad request"}), 400)

    # the remaining commands require city id, so check for id field
    if not payload:
        return make_response(jsonify({"error": "invalid json data"}), 400)

    ret = weather.get_count(payload, city_id)

    if ret["status"] == "error":
        return make_response(JSONEncoder().encode(ret), ret["code"])
    else:
        return make_response(JSONEncoder().encode(ret), 200)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'not found'}), 404)
