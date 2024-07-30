import zmq
import json
import sys

CO2_INPUT_PORT = 5555
IP_ADD = "127.0.0.1"

co2_data_log = "co2_data.log"


def process_co2_data():
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://{}:{}".format(IP_ADD, CO2_INPUT_PORT))
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "co2")

    while True:
        message = subscriber.recv_string()
        print("Received weather data:", message)
        data = json.loads(message.split(" ", 1)[1])
        with open(co2_data_log, "a") as file:
            file.write(json.dumps(data) + "\n")

        if data["co2"] > 400:
            print("Danger Zone! Please do not leave home")


def main():
    try:
        process_co2_data()
    except KeyboardInterrupt:
        print("^CTerminating data_processor")


if __name__ == "__main__":
    main()
