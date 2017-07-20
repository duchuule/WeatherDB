from flask import Flask, make_response, request
from model import JSONEncoder, Model

app = Flask(__name__)
model = Model("mongo")


# api to get weather data
@app.route('/', methods=['GET'])
def get_data():
    db = model.get_db()
    try:
        if not request.json:
            return JSONEncoder().encode({"error": "invalid json data"})
    except Exception as e:
        # note: this will happen if json data do not escape the quotes around "count", "time", etc (on windows)
        return JSONEncoder().encode({"error": "invalid json data", "exception": str(e)})

    # these commands do not require cityid
    if 'count' in request.json:
        if request.json['count'] == 'all':  # requesting sum total number of entries in database
            return JSONEncoder().encode({"count": db.count()})
        else:  # requesting only number of entries for 1 city
            cityid = request.json['count']
            return JSONEncoder().encode(db.find({"id": cityid}).count())

    # the remaining commands require city id, so check for id field
    if 'id' not in request.json:
        return JSONEncoder().encode({"error": "invalid json data"})

    cityid = request.json["id"]

    # when 'time' is requested, return one data point closest to that time
    if 'time' in request.json:
        return JSONEncoder().encode(model.find_closest(request.json['time'], cityid))
    # when users request data for an a time interval
    elif 'begintime' in request.json and 'endtime' in request.json:
        return JSONEncoder().encode(model.find_interval(request.json['begintime'], request.json['endtime'], cityid))
    else:
        return JSONEncoder().encode({"error": "no time specified"})


@app.errorhandler(404)
def not_found():
    return make_response(JSONEncoder().encode({'error': 'not found'}), 404)


@app.errorhandler(400)
def bad_request():
    return make_response(JSONEncoder().encode({'error': 'bad request'}), 400)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
