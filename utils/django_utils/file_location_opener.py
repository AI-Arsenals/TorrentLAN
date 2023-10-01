import subprocess
import os
import platform
import time
from utils.log.main import log

def open_file_location(file_location,BASE_DIR):
    # check if BASE_DIR is in file_location
    if not (BASE_DIR in file_location):
        file_location=os.path.join(BASE_DIR,file_location)
    file_location=os.path.realpath(file_location)

    # check if BASE_DIR is in file_location
    if not (BASE_DIR in file_location):
        log("file_location_opener : file_location is not in BASE_DIR",2)
        # report suspicious activity
        return False
    # if(os.path.isfile(file_location)):
        # os.startfile(file_location)
    # else:
        # one_dir_back=os.path.dirname(file_location)
        # # highlight file in explorer
        # os.startfile(one_dir_back)

    if platform.system()=='Windows':
        # import ctypes
        # process = subprocess.Popen(['start', file_location], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # hwnd=ctypes.windll.user32.FindWindowW(None, file_location)
        # # bring window to front
        # user32 = ctypes.windll.user32
        # user32.ShowWindow(hwnd, 9)
        os.startfile(file_location)
    else:
        os.startfile(file_location)
    return True