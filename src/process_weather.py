import zmq
import json
import sys
import threading
from datetime import datetime, timedelta

WEATHER_INPUT_PORT = 5555
FASHION_SOCKET_PORT = 5556

IP_ADD = "127.0.0.1"

latest_data = {"temperature": 0, "humidity": 0, "average-temp": 0, "average-hum": 0}

weather_data_log = "weather_data.log"


def average_temperature_humidity():
    global latest_data
    now = datetime.now()
    start_time = now - timedelta(seconds=30)
    temp_sum = 0
    hum_sum = 0
    count = 0

    with open(weather_data_log, "r") as file:
        for line in file:
            data = json.loads(line)
            data_time = datetime.strptime(data["time"], "%Y-%m-%d %H:%M:%S")
            if start_time <= data_time <= now:
                temp_sum += data["temperature"]
                hum_sum += data["humidity"]
                count += 1

    if count > 0:
        latest_data["average-temp"] = round(temp_sum / count, 2)
        latest_data["average-hum"] = round(hum_sum / count, 2)


def recommendation():
    result = ""
    average_temperature_humidity()
    if latest_data["average-temp"] < 10:
        result = "Today weather is cold. Its better to wear warm clothes"
    elif latest_data["average-temp"] > 10 and latest_data["average-temp"] < 25:
        result = "Feel free to wear spring/autumn clothes"
    else:
        result = "Go for light clothes"
    print(result)
    return result


def report():
    average_temperature_humidity()
    result = f"The last 30 sec average Temperature is {latest_data['average-temp']} and Humidity {latest_data['average-hum']}"
    print(result)
    return result


def client_handler():
    context = zmq.Context()
    fashion_socket = context.socket(zmq.REP)
    fashion_socket.bind("tcp://{}:{}".format(IP_ADD, FASHION_SOCKET_PORT))

    while True:
        request = fashion_socket.recv_string()
        if request == "Fashion":
            fashion_socket.send_string(recommendation())
        elif request == "Weather":
            fashion_socket.send_string(report())
        else:
            fashion_socket.send_string("Query Not Found")


def weather_data_receiver():
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://{}:{}".format(IP_ADD, WEATHER_INPUT_PORT))
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "weather")

    while True:
        try:
            message = subscriber.recv_string()
            print("Received weather data:", message)
            data = json.loads(message.split(" ", 1)[1])
            with open(weather_data_log, "a") as file:
                file.write(json.dumps(data) + "\n")

        except KeyboardInterrupt:
            print("^CTerminating data_processor")
            subscriber.close()
            context.term()


def main():
    client_thread = threading.Thread(target=client_handler)
    weather_thread = threading.Thread(target=weather_data_receiver)

    client_thread.start()
    weather_thread.start()

    client_thread.join()
    weather_thread.join()


if __name__ == "__main__":
    main()
