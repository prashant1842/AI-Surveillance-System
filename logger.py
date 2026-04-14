import datetime

LOG_FILE = "logs.txt"

def log_data(detected_objects, risk):
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_line = f"{time_now} | Objects: {detected_objects} | Risk: {risk}\n"

    with open(LOG_FILE, "a") as f:
        f.write(log_line)