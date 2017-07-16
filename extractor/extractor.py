from threading import Thread, Event
import datetime


class Scheduler(Thread):
    def __init__(self, _event, _script, _delay=2):
        Thread.__init__(self)
        self.event = _event
        self.script = _script
        self.delay = _delay

    def run(self):
        while not self.event.is_set():
            self.script()
            self.event.wait(self.delay)


def printtime():
    print(datetime.datetime.now())

if __name__ == "__main__":
    stopEvent = Event()
    schedule = Scheduler(stopEvent, printtime, 10)
    schedule.start()


