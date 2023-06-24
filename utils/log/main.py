import datetime
import os
import json
import sys
from termcolor import colored, cprint

CONFIG_FILE="configs/log_config.json"

class DebugModule:
    def __init__(self, file_name='log.txt'):
        log_location_set()
        LOGS_FILE_PATH = json.load(open(CONFIG_FILE))["logs_file_path"]
        self.file_path = os.path.join(LOGS_FILE_PATH, file_name)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                f.write("")

    def log_message(self, message, severity_no=0, script_name=None):
        severities = {0: "INFO", 1: "WARNING", 2: "ERROR"}
        severity = severities.get(severity_no, "info")

        color_map = {0: 'green', 1: 'yellow', 2: 'red'}
        color = color_map.get(severity_no, 'white')

        try:
            module_name = script_name
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"[{current_time}] [{module_name}] [{severity.upper()}] {message}\n"

            with open(self.file_path, 'a') as file:
                file.write(log_message)

            print(colored(f"[{severity.upper()}] {message}", color))
        except IOError:
            print(colored(f"Error: Unable to write to file: {self.file_path}", 'red'))

    def show_logs(self):
        try:
            with open(self.file_path, 'r') as file:
                print(file.read())
        except IOError:
            print(colored(f"Error: Unable to read file: {self.file_path}", 'red'))

def log(msg, severity_no=0, *args,file_name='log.txt'):
    logger = DebugModule(file_name)
    calling_script_path = os.path.abspath(sys.argv[0])
    root_dir_index = calling_script_path.find("TorrentLAN")

    if root_dir_index != -1:
        calling_script_name = calling_script_path[root_dir_index:]
    else:
        calling_script_name = calling_script_path
        
    logger.log_message(msg, severity_no, calling_script_name)




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
    log("testing",1)
