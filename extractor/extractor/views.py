from flask import jsonify, abort, make_response, request
from threading import Event
from .extract import Extractor, Scheduler
import os
import pymongo
from extractor import config
import werkzeug.exceptions as exceptions

from extractor.flask_app import app

stop_event = Event()  # event handle to stop the scheduler

app.config.from_object(config)

# initialize the extractor object
extractor = None

def connect_db():
    host = os.getenv('DBHOST', "localhost")  # host name will be set by docker through environment variable if needed
    dbname = os.getenv('DBNAME', 'weatherdb')  # database name will be set by test cases if needed
    db = pymongo.MongoClient(host)[dbname]
    global extractor
    extractor = Extractor(app.config["CITIES"], db, app.config["API_KEY"])

# connect to database
connect_db()

schedule = Scheduler(stop_event, extractor.get_weather, app.config["DELAY"])
schedule.daemon = True
schedule.start()

# query current config
@app.route('/', methods=['GET'])
def get_config():
    # build a list of public config
    ret = dict(CITIES=app.config["CITIES"], DELAY=app.config["DELAY"])
    return jsonify(ret)


# query number of record in database
@app.route('/db', methods=['GET'])
def get_db_info():
    return jsonify({'count': extractor.get_db().count()})


# change configuration of the server
@app.route('/config', methods=['PUT'])
def set_config():
    try:
        payload = request.get_json()
    # BadRequest exception will be raised if json data is not formated properly
    # and decoding of json data failed.
    except exceptions.BadRequest as e:
        return make_response(jsonify({"error": "bad request"}), 400)

    if 'delay' in payload:
        if app.config["DELAY"] != request.json['delay']:
            app.config["DELAY"] = request.json['delay']
            global stop_event
            stop_event.set()
            stop_event = Event()
            new_schedule = Scheduler(stop_event, extractor.get_weather, app.config["DELAY"])
            new_schedule.daemon = True
            new_schedule.start()
    return jsonify(dict(DELAY=app.config["DELAY"]))


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'bad request'}), 400)