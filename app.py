from datetime import datetime, timedelta
from flask import Flask, jsonify
import requests
from prometheus_client import CollectorRegistry, Counter, Gauge, make_wsgi_app, generate_latest 

app = Flask(__name__)

APP_VERSION = "0.0.1"
TARGET_ID = "5eba5fbad46fb8001b799786"

# Create the CollectorRegistry instance
REGISTRY = CollectorRegistry()

# Define metrics
request_count = Counter("request_count", "Total number of requests served", registry=REGISTRY)
last_temperature = Gauge("last_temperature", "Last measured temperature", registry=REGISTRY)


@app.route("/")
def index():
    return __name__

@app.route("/version")
def version():
    return APP_VERSION

@app.route("/temperature")
def temperature():
    r = requests.get(f"https://api.opensensemap.org/boxes/{TARGET_ID}?format=json", timeout=600)
    data = r.json()
    temps = data["sensors"]

    avg_temperature = ""
    time_of_request = ""

    for temp in temps:
        if temp["title"] == "Temperatur":
            avg_temperature = temp['lastMeasurement']['value']
            time_of_request = temp['lastMeasurement']['createdAt']

    lasttime_datatime = datetime.strptime(time_of_request, "%Y-%m-%dT%H:%M:%S.%fZ")
    timenow = datetime.now()

    if timenow - lasttime_datatime > timedelta(hours=1):
        return "Data could not be returned as it exceeds 1 hour"

    status = get_temperature_status(float(avg_temperature))
    request_count.inc()  
    last_temperature.set(float(avg_temperature))  
    return jsonify({"temperature": avg_temperature, "status": status})

def get_temperature_status(temperature):
    if temperature < 10:
        return "Too Cold"
    elif 11 <= temperature <= 36:
        return "Good"
    else:
        return "Too Hot"

@app.route("/metrics")
def metrics():
    return make_wsgi_app(REGISTRY)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
