import shutil
import os

TMP_FOLDERS=["./data/.tmp_download","./data/Web_downloader/tmp"]

def fetch_tmp_size():
    TOTAL_SIZE=0
    for folder in TMP_FOLDERS:
        if not os.path.exists(folder):
            continue
        TOTAL_SIZE+=shutil.disk_usage(folder).used
    return TOTAL_SIZE

def delete_tmp():
    for folder in TMP_FOLDERS:
        if not os.path.exists(folder):
            continue
        shutil.rmtree(folder)

if __name__ == "__main__":
    print(fetch_tmp_size())
    delete_tmp()