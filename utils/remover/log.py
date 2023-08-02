import shutil
import os

LOG_FOLDER="./data/.logs"

def fetch_logs_size():
    if not os.path.exists(LOG_FOLDER):
        return 0

    total_size = 0

    for dirpath, dirnames, filenames in os.walk(LOG_FOLDER):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)

    return total_size

def delete_logs():
    if not os.path.exists(LOG_FOLDER):
        return
    shutil.rmtree(LOG_FOLDER)

if __name__ == "__main__":
    print(fetch_logs_size())
    # delete_logs()