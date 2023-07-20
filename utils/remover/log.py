import shutil
import os

LOG_FOLDER="./data/.logs"

def fetch_logs_size():
    if not os.path.exists(LOG_FOLDER):
        return 0
    total_size = shutil.disk_usage(LOG_FOLDER).used
    return total_size

def delete_logs():
    if not os.path.exists(LOG_FOLDER):
        return
    shutil.rmtree(LOG_FOLDER)

if __name__ == "__main__":
    print(fetch_logs_size())
    delete_logs()