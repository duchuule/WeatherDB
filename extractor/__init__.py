from flask import Flask, jsonify, abort, make_response, request
from threading import Event
from extract import Extractor, Scheduler
import os

app = Flask(__name__)
stop_event = Event()  # event handle to stop the scheduler

app.config.from_pyfile("config.py")
# initialize the extractor object
# if using docker, the host name will be set to a value other than localhost
extractor = Extractor(app.config["CITIES"], os.getenv('DBHOST', "localhost"),
                      app.config["API_KEY"])


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
    if not request.json:
        abort(400)
    if 'delay' in request.json:
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
def not_found():
    return make_response(jsonify({'error': 'not found'}), 404)


@app.errorhandler(400)
def bad_request():
    return make_response(jsonify({'error': 'bad request'}), 400)


if __name__ == "__main__":
    schedule = Scheduler(stop_event, extractor.get_weather, app.config["DELAY"])
    schedule.daemon = True
    schedule.start()
    app.run(host='0.0.0.0', port=5000)
