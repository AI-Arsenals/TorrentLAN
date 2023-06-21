import uuid
import os 
import json

CONFIG="configs/identity.json"

def generate_client_id():
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
            return

def set_user_name(user_name=None):
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
    return
    
if __name__=='__main__':
    generate_client_id()
    set_user_name()
