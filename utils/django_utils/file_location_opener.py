import os
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
    os.startfile(file_location)
    return True