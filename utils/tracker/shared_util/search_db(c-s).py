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


def search_db(search_bys,searchs):
    ip = get_ip_address(SERVER_ADDR)
    try:
        # Connect to server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(60)
            log(f"Connecting to {ip} for searching with the filter {zip(search_bys,searchs)}")
            s.connect((ip, PORT))
            log("Connected to server")
            js_data = {}
            js_data["search_db"]=True
            js_data["search_bys"]=search_bys
            js_data["searchs"]=searchs
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
            results=json_returned_data["results"]
            s.close()
        return results
    except socket.timeout:
        log("Connection timed out", 2)
        log("Server is down", 2)
        return False
    except ConnectionRefusedError:
        log("Server is down", 2)
        return False
if __name__ == '__main__':
    log(search_db(["name","unique_id"],["main","4e3df847-b2af-49a6-bec3-1784fab047e2"]))
