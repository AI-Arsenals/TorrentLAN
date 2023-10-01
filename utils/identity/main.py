import uuid
import os 
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from utils.log.main import log

CONFIG="configs/identity.json"

def create_data_folders():
    try:
        folders=["Games", "Movies", "Music", "Pictures", "Documents","College","Others"]
        for folder in folders:
            if not os.path.exists(os.path.join("data","Normal", folder)):
                os.makedirs(os.path.join("data","Normal", folder))
                log(f"Created folder {folder} in data")
        return True
    except Exception as e:
        log(f"Error in creating data folders; error=: {e}")
        return False


def generate_client_id():
    create_data_folders()
    try:
        if not os.path.exists(CONFIG):
            with open(CONFIG, 'w') as f:
                json.dump({}, f)
        
        with open(CONFIG, 'r') as f:
            data = json.load(f)
            if 'client_id' in data:
                return
            else:
                client_id = str(uuid.uuid4())
                data['client_id'] = client_id
                with open(CONFIG, 'w') as f:
                    json.dump(data, f)
                log(f"Generated client id={client_id}")
                return
    except Exception as e:
        log(f"Error in generating client id; error=: {e}")
        return False

def set_user_name(user_name=None):
    try:
        if not os.path.exists(CONFIG):
            with open(CONFIG, 'w') as f:
                json.dump({}, f)
        
        with open(CONFIG, 'r') as f:
            data = json.load(f)
        if user_name is None:
            generate_client_id()
            user_name = "PC_"+data['client_id']
        data['user_name'] = user_name
        with open(CONFIG, 'w') as f:
            json.dump(data, f)
        log(f"Set user name={user_name}")
        return True
    except Exception as e:
        log(f"Error in setting user name as{user_name}; error=: {e}")
        return False
    
def show_user_name():
    try:
        with open(CONFIG, 'r') as f:
            data = json.load(f)
        return data['user_name']
    except Exception as e:
        log(f"Error in showing user name; error=: {e}")
        return ""
    
if __name__=='__main__':
    generate_client_id()
    set_user_name()
