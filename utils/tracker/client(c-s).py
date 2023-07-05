import socket
import os
import sys
import json
import base64
import importlib.util as import_util

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from utils.log.main import log

module_path = "utils/tracker/client_ip_reg(c-s).py"
spec =import_util.spec_from_file_location("", module_path)
module =import_util.module_from_spec(spec)
spec.loader.exec_module(module)
get_ip_address=getattr(module, "get_ip_address")

CONFIG_IDENTITY = "configs/identity.json"
CONFIG_CLIENT = "configs/client(c-s).json"
OWN_UNIQUE_ID = json.load(open(CONFIG_IDENTITY))["client_id"]
DBS_LOCATION = "./data/.db/file_tree.db"
SERVER_CONFIG="configs/server.json"
SERVER_ADDR=json.load(open(SERVER_CONFIG))["server_addr"]

PORT = json.load(open(SERVER_CONFIG))["server_port"]

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
            data_to_send = json.dumps(js_data).encode()
            data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>" #"<"+ sha256 of "<EOF>"+">"
            s.sendall(data_to_send)
        s.close()
        return True
    except ConnectionRefusedError:
        log("Server is down",2)
        return False

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
    check_updation()
