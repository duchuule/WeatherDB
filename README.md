# WeatherDB
A service that periodically collects weather data from OpenWeatherMap and provides API for data retrieval

1. Extractor service is run on port 5000. When run, it collects weather data from 5 largest cities every minute. The data collection interval can be changed with a PUT request.

2. Gatekeeper service is run on port 80. Here are some of the supported APIs, using curl on Windows:

curl -i "http://localhost/db"

curl -i "http://localhost/db/4699066"

curl -i -H "Content-Type: application/json" -X "GET" -d "{\\"time\\":1500273432}" "http://localhost/weather/4699066"

curl -i -H "Content-Type: application/json" -X "GET" -d "{\\"time\\":\\"2017-07-17T04:07:25\\"}" "http://localhost/weather/4699066"

curl -i -H "Content-Type: application/json" -X "GET" -d "{\\"begintime\\":1500318000,\\"endtime\\":1500319800}" "http://localhost/weather/4699066"

where: - the last number in url is cityid

       - "time", "begintime", "endtime" can be unix timestamp (integer type) or ISO 8601 string in UTC timezone
