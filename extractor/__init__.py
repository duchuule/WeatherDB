from flask import Flask, jsonify, abort, make_response, request
from threading import Event
from extract import Extractor, Scheduler

cities = [{"id": 4699066, "name": "Houston"},
          {"id": 5128581, "name": "New York"},
          {"id": 5368361, "name": "Los Angeles"},
          {"id": 4887398, "name": "Chicago"},
          {"id": 5308655, "name": "Phoenix"}
          ]  # list of cities to collect weather data
app = Flask(__name__)
stop_event = Event()  # event handle to stop the scheduler
config = {"delay": 60}  # default server config
API_KEY = "a40f16f6c2b566534b10c2bb5553994b"
extractor = Extractor(cities, "mongo", API_KEY)


# query current config
@app.route('/', methods=['GET'])
def get_config():
    return jsonify(config)


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
        if config["delay"] != request.json['delay']:
            config["delay"] = request.json['delay']
            global stop_event
            stop_event.set()
            stop_event = Event()
            new_schedule = Scheduler(stop_event, extractor.get_weather, config["delay"])
            new_schedule.daemon = True
            new_schedule.start()
    return jsonify(config)


@app.errorhandler(404)
def not_found():
    return make_response(jsonify({'error': 'not found'}), 404)


@app.errorhandler(400)
def bad_request():
    return make_response(jsonify({'error': 'bad request'}), 400)


if __name__ == "__main__":
    schedule = Scheduler(stop_event, extractor.get_weather, config["delay"])
    schedule.daemon = True
    schedule.start()
    app.run(host='0.0.0.0', port=5000)
