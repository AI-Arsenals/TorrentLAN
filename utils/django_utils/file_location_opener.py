import subprocess
import os
import platform
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
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

if __name__=='__main__':
    open_file_location(r'data/Normal/College/AI_2025/WIN_20230823_17_32_29_Pro.jpg',r'C:\\Users\\prakh\\AppData\\Local\\TorrentLAN')