import os
import requests
import time
import logging
from prometheus_client import start_http_server, Gauge

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s  %(message)s')

hub_url = os.environ.get("hub_url")
hub_user = os.environ.get("hub_user")
hub_password = os.environ.get("hub_password")
hub_type = os.environ.get("hub_type", "HC3") # to add more hubs in the future
enabled = os.environ.get("enabled", "True") == "True" # show only enabled devices
visible = os.environ.get("visible", "True") == "True" # show only visible devices
update_interval = os.environ.get("update_interval", "60")

if hub_url is None:
    logging.error("Hub url is not defined. Set environment variable 'hub_url'")
    exit(1)
if hub_url is None:
    logging.error("Hub user is not defined. Set environment variable 'hub_user'")
    exit(1)
if hub_url is None:
    logging.error("Hub password is not defined. Set environment variable 'hub_password'")
    exit(1)
if not update_interval.isdigit():
    logging.error("'update_interval' must be a digit only")
    exit(1)

def request(url):
    count = 0
    ok = False
    while not ok:
        count += 1
        if count > 5:
            logging.error("Request attempts exceeded")
            exit(1)
        try:
            r = session.get(url)
        except Exception as e:
            logging.error(e)
            time.sleep(update_interval_int)
            continue
        if not r.ok:
            logging.error(f"request to '{r.url}'")
            logging.error(f"code: {r.status_code}")
            logging.error(f"reason: {r.reason}\n")
            time.sleep(update_interval_int)
            continue
        ok = True
    return r

update_interval_int = int(update_interval)
session = requests.Session()
session.auth = (hub_user, hub_password)
start_http_server(8000)
logging.info(f"Start export from hub {hub_url}")

if hub_type == "HC3":
    logging.info(f"Hub type is {hub_type}")


    rooms = {}
    count = 0
    labelnames=['device_id', 'device_name', 'room_id', "room_name", "device_type"]
    batteryLevel = Gauge(name="fibaro_battery_level", documentation="", labelnames=labelnames )
    energy = Gauge(name="fibaro_energy", documentation="", labelnames=labelnames )
    power = Gauge(name="fibaro_power", documentation="", labelnames=labelnames )
    value = Gauge(name="fibaro_value", documentation="", labelnames=labelnames )
    value2 = Gauge(name="fibaro_value2", documentation="", labelnames=labelnames )

    while True:

        # periodic reset of room names
        count += 1
        if count > 60:
            count = 0
            rooms = {}

        r = request( hub_url + "/api/devices")

        for device in r.json():
            if device.get("enabled") == enabled:
                if device.get("visible") == visible:

                    if device["roomID"] in rooms:
                        room_name =  rooms[device["roomID"]]
                    else:
                        room_r = request( hub_url + "/api/rooms")
                        rooms = {}
                        for room in room_r.json():
                            rooms[room["id"]] = room["name"]
                        room_name = rooms.get(device["roomID"] , "unknown")

                    device_batteryLevel = device.get("properties",{}).get("batteryLevel")
                    if device_batteryLevel is not None:
                        batteryLevel.labels(
                            device_id=device["id"],
                            device_name=device["name"],
                            room_id=device["roomID"],
                            room_name=room_name,
                            device_type=device["type"]
                        ).set(device_batteryLevel)

                    device_energy = device.get("properties",{}).get("energy")
                    if device_energy is not None:
                        energy.labels(
                            device_id=device["id"],
                            device_name=device["name"],
                            room_id=device["roomID"],
                            room_name=room_name,
                            device_type=device["type"]
                        ).set(device_energy)

                    device_power = device.get("properties",{}).get("power")
                    if device_power is not None:
                        power.labels(
                            device_id=device["id"],
                            device_name=device["name"],
                            room_id=device["roomID"],
                            room_name=room_name,
                            device_type=device["type"]
                        ).set(device_power)

                    device_value = device.get("properties",{}).get("value")
                    if device_value is not None:
                        value.labels(
                            device_id=device["id"],
                            device_name=device["name"],
                            room_id=device["roomID"],
                            room_name=room_name,
                            device_type=device["type"]
                        ).set(device_value)

                    device_value2 = device.get("properties",{}).get("value2")
                    if device_value2 is not None:
                        value2.labels(
                            device_id=device["id"],
                            device_name=device["name"],
                            room_id=device["roomID"],
                            room_name=room_name,
                            device_type=device["type"]
                        ).set(device_value2)

        time.sleep(update_interval_int)

else:
    logging.error(f"Unknown hub type ({hub_type})")
    exit(1)
