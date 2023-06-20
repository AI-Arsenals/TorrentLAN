import socket
import os
import sys
import json
import base64

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from utils.log.main import log

CONFIG_IDENTITY = "configs/identity.json"
CONFIG_CLIENT = "configs/client(c-s).json"
OWN_UNIQUE_ID = json.load(open(CONFIG_IDENTITY))["client_id"]
DBS_LOCATION = "./data/.db/file_tree.db"
SERVER_CONFIG="configs/server.json"
SERVER_ADDR=json.load(open(SERVER_CONFIG))["server_addr"]

PORT = 8888

def update_server(unique_id, ip):
    try:
        # Connect to server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            log(f"Connecting to server at {ip}")
            s.connect((ip, PORT))
            log("Connected to server")
            js_data = {}
            js_data["unique_id"] = unique_id
            js_data["db_update"] = True
            with open(DBS_LOCATION, "rb") as f:
                js_data["db_data"] = base64.b64encode(f.read()).decode()
            data_to_send = json.dumps(js_data)
            data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>" #"<"+ sha256 of "<EOF>"+">"
            s.sendall(data_to_send.encode())
        s.close()
        return True
    except ConnectionRefusedError:
        log("Server is down",2)
        return False

def get_ip_address(address):
    try:
        ip_address = socket.gethostbyname(address)
        return ip_address
    except socket.gaierror:
        return None

def check_updation(Force_update=False):
    ip = get_ip_address(SERVER_ADDR)
    mtime = os.stat(DBS_LOCATION).st_mtime

    if not os.path.exists(CONFIG_CLIENT):
        with open(CONFIG_CLIENT, 'w') as f:
            json.dump({"Last_Sent": mtime}, f)
        success = update_server(OWN_UNIQUE_ID, ip)
        if success:
            log("Successfully updated server")
            with open(CONFIG_CLIENT, 'w') as f:
                json.dump({"Last_Sent": mtime}, f)
        else:
            os.unlink(CONFIG_CLIENT)
    else:
        with open(CONFIG_CLIENT, 'r') as f:
            data = json.load(f)
            last_sent = data.get("Last_Sent",None)
            if last_sent is None or last_sent != mtime or Force_update:
                success = update_server(OWN_UNIQUE_ID, ip)
                if success:
                    log("Successfully updated server")
                    with open(CONFIG_CLIENT, 'w') as f:
                        json.dump({"Last_Sent": mtime}, f)
            else:
                log("Already Upto date")
if __name__ == '__main__':
    check_updation(Force_update=True)
