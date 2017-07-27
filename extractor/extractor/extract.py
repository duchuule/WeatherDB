import pymongo
from threading import Thread
import datetime
import requests
import math


class Scheduler(Thread):
    """Class to perform periodic task, with an event to stop"""

    def __init__(self, event, script, delay=2):
        Thread.__init__(self)
        self._event = event
        self._script = script
        self._delay = delay

    def run(self):
        while not self._event.is_set():
            self._script()
            self._event.wait(self._delay)


class Extractor:
    """Class to perform data extracting from OpenWeatherMap"""

    def __init__(self, cities, database, api_key):
        self._cities = cities
        self._db = database
        self._api_key = api_key

    def get_db(self):
        coll = self._db["weather"]
        return coll

    def get_weather(self):
        try:
            new_entries = []
            for city in self._cities:
                r = requests.get(
                    'http://api.openweathermap.org/data/2.5/weather?id=' + str(city["id"]) + "&APPID=" + self._api_key)
                entry = r.json()
                entry["source"] = "OpenWeatherMap"
                dt = datetime.datetime.now(datetime.timezone.utc)  # do *not* use utcnow()!
                entry["updated_on"] = math.floor(dt.timestamp())
                new_entries.append(entry)
                # print(entry)

            # add entries in batch
            coll = self.get_db()
            coll.insert_many(new_entries)
        except Exception as e:
            print("Exception: ", e)

            # def print_time():
            #     print(datetime.datetime.now())
