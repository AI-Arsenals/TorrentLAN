import socket
import os
import json
import sys
import importlib.util as import_util

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..')))
from utils.log.main import log

module_path = "utils/tracker/client_ip_reg(c-s).py"
spec =import_util.spec_from_file_location("", module_path)
module =import_util.module_from_spec(spec)
spec.loader.exec_module(module)
get_ip_address=getattr(module, "get_ip_address")

SERVER_CONFIG="configs/server.json"
SERVER_ADDR=json.load(open(SERVER_CONFIG))["server_addr"]

PORT = json.load(open(SERVER_CONFIG))["server_port"]


def get_ips_and_netmasks(unique_ids):
    ip = get_ip_address(SERVER_ADDR)
    try:
        # Connect to server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(60)
            log(f"Connecting to {ip} for fetching ips and netmasks from unique ids")
            s.connect((ip, PORT))
            log("Connected to server")
            js_data = {}
            js_data["ip_get"]=True
            js_data["unique_ids"] = unique_ids
            data_to_send = json.dumps(js_data).encode()
            data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>" #"<"+ sha256 of "<EOF>"+">"
            s.sendall(data_to_send)

            # Receive data
            data=b""
            while True:
                chunk = s.recv(1024)
                if not chunk:
                    break
                data+=chunk
                if data.endswith(b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"): #"<"+ sha256 of "<EOF>"+">"
                    data = data[:-66]  # Remove termination sequence from the data
                    break
            json_returned_data = json.loads(data.decode())
            s.close()
        return True,json_returned_data
    except socket.timeout:
        log("Connection timed out", 2)
        log("Server is down", 2)
        return False,None
    except ConnectionRefusedError:
        log("Server is down", 2)
        return False,None
if __name__ == '__main__':
    get_ips_and_netmasks("041279ea-3370-40a8-a094-e9cbb5a389f2")
