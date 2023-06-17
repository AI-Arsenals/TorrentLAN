import datetime
import inspect
import os
import json

CONFIG_FILE="configs/log_config.json"

class DebugModule:
    def __init__(self, file_name='log.txt'):
        LOGS_FILE_PATH = json.load(open(CONFIG_FILE))["logs_file_path"]
        self.file_path = os.path.join(LOGS_FILE_PATH, file_name)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                f.write("")

    def log_message(self, message, severity_no=0):
        severities={0:"info",1:"warning",2:"error"}
        severity=severities.get(severity_no,"info")
        print(message)
        try:
            module_name = inspect.stack()[1].filename
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"[{current_time}] [{module_name}] [{severity.upper()}] {message}\n"

            with open(self.file_path, 'a') as file:
                file.write(log_message)

            # print(f"Logged message with severity '{severity}' to file: {self.file_path}")
        except IOError:
            print(f"Error: Unable to write to file: {self.file_path}")

    def show_logs(self):
        try:
            with open(self.file_path, 'r') as file:
                print(file.read())
        except IOError:
            print(f"Error: Unable to read file: {self.file_path}")

def log(msg):
    logger=DebugModule("log.txt")
    logger.log_message(msg)

def show_logs():
    logger=DebugModule("log.txt")
    logger.show_logs()

def log_location_set():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"logs_file_path": os.path.join(os.getcwd(),"data", ".logs")}, f)

    LOGS_FILE_PATH = json.load(open(CONFIG_FILE))["logs_file_path"]
    if not os.path.exists(LOGS_FILE_PATH):
        os.makedirs(LOGS_FILE_PATH)
    if not os.path.exists(os.path.join(LOGS_FILE_PATH, "log.txt")):
        with open(os.path.join(LOGS_FILE_PATH, "log.txt"), "w") as f:
            f.write("")

if __name__ == '__main__':
    log_location_set()
