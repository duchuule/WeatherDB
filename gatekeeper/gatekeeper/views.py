from flask import make_response, request, jsonify
from .model import Weather, JSONEncoder
import werkzeug.exceptions as exceptions

import os
import pymongo

from gatekeeper import app




_host = os.getenv('DBHOST', "localhost")  # host name will be set by docker through environment variable if needed
_db = pymongo.MongoClient(_host)['weatherdb']
weather = Weather(_db)


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

    db = weather.get_db()

    # when 'time' is requested, return one data point closest to that time
    if 'time' in request.json:
        return JSONEncoder().encode(weather.find_closest(request.json['time'], city_id))
    # when users request data for an a time interval
    elif 'begintime' in request.json and 'endtime' in request.json:
        return JSONEncoder().encode(weather.find_interval(request.json['begintime'], request.json['endtime'], city_id))
    else:
        return make_response(jsonify({"error": "no time specified"}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'not found'}), 404)

