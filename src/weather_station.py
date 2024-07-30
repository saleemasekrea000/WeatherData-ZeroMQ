import sys
import zmq
import time
import json
import random
from datetime import datetime

IP_ADD = "127.0.0.1"
DATA_PROCESSING_INPUT_PORT = 5555


def generate_weather_data():
    temperature = round(random.uniform(5, 40), 1)
    humidity = round(random.uniform(40, 100), 1)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    weather_data = {
        "time": current_time,
        "temperature": temperature,
        "humidity": humidity,
    }
    return weather_data


def generate_co2_data():
    co2_level = round(random.uniform(300, 500), 1)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    co2_data = {"time": current_time, "co2": co2_level}
    return co2_data


def main():
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind("tcp://{}:{}".format(IP_ADD, DATA_PROCESSING_INPUT_PORT))

    try:
        time.sleep(2)

        while True:
            weather_data = generate_weather_data()
            co2_data = generate_co2_data()

            publisher.send_string("weather " + json.dumps(weather_data))
            print("Weather is sent from WS1", weather_data)
            publisher.send_string("co2 " + json.dumps(co2_data))
            print("CO2 is sent from WS1", co2_data)

            time.sleep(2)

    except KeyboardInterrupt:
        print("^CTerminating data_processor")
        publisher.close()
        context.term()


if __name__ == "__main__":
    main()
