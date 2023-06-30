import socket
import os
import json
import sys
import importlib.util as import_util

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from utils.log.main import log

module_path = "utils/tracker/client_ip_reg(c-s).py"
spec =import_util.spec_from_file_location("", module_path)
module =import_util.module_from_spec(spec)
spec.loader.exec_module(module)
get_my_connect_ip=getattr(module, "get_my_connect_ip")
get_ip_address=getattr(module, "get_ip_address")


SERVER_CONFIG="configs/server.json"
SERVER_ADDR=json.load(open(SERVER_CONFIG))["server_addr"]

PORT = json.load(open(SERVER_CONFIG))["server_port"]

def fetch_unique_id_from_hashes(hashes):
    ip = get_ip_address(SERVER_ADDR)
    log(f"Connecting to {ip} for fetching ids from hashes")
    try:
        # Connect to server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(30)
            s.connect((ip, PORT))
            log("Connected to server")
            js_data = {}
            js_data["hash_to_id"] = True
            js_data["hashes"] = hashes
            data_to_send = json.dumps(js_data).encode()
            data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>" #"<"+ sha256 of "<EOF>"+">"
            s.sendall(data_to_send)

            # Receive data from server
            data=b""
            while True:
                chunk = s.recv(1024*500)
                if not chunk:
                    break
                data += chunk
            if data.endswith(b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"): #"<"+ sha256 of "<EOF>"+">"
                data = data[:-66]  # Remove termination sequence from the data
            else:
                log(f"Termination sequence not found in data from {ip}")
                s.close()
                return False
            data = json.loads(data)
            return data
    except socket.timeout:
        log("Connection timed out",2)
        log("Server is down",2)
        return False
    except ConnectionRefusedError:
        log("Server is down",2)
        return False

if __name__ == '__main__':
    log(fetch_unique_id_from_hashes(["fae379b2920b02b4c85110eb4d3f42a9997e669c96b15423f9af8cdfd9775098","51cc3d41a2afb83c383de8a8f4832d40b1a60553cdaa82883db284e9fed64c7c"]))
    

