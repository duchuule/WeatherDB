from flask import Flask, jsonify, abort, make_response, request, url_for
import pymongo
from threading import Thread, Event
import datetime
import requests

cities = [{"id": 4699066, "name": "Houston"},
          {"id": 5128581, "name": "New York"},
          {"id": 5368361, "name": "Los Angeles"},
          {"id": 4887398, "name": "Chicago"},
          {"id": 5308655, "name": "Phoenix"}
          ] # list of cities to collect weather data
app = Flask(__name__)
stop_event = Event() # event handle to stop the scheduler
config = {"delay":60} # default server config

class Scheduler(Thread):
    def __init__(self, event, script, delay=2):
        Thread.__init__(self)
        self._event = event
        self._script = script
        self._delay = delay

    def run(self):
        while not self._event.is_set():
            self._script()
            self._event.wait(self._delay)


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
            new_schedule = Scheduler(stop_event, print_time, config["delay"])
            new_schedule.start()
    return jsonify(config)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


# def get_weather():
#     r = requests.get('http://api.openweathermap.org/data/2.5/weather?id=4699066&APPID=a40f16f6c2b566534b10c2bb5553994b')
#     print(r.json())


def print_time():
    print(datetime.datetime.now())

if __name__ == "__main__":
    schedule = Scheduler(stop_event, print_time, config["delay"])
    schedule.start()
    app.run(port=5000)


