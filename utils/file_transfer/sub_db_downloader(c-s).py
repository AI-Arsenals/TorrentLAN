import socket
import os
import json
import sys
import base64
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
SUB_DB_PATH = "data/.db/sub_db_downloaded"

PORT = json.load(open(SERVER_CONFIG))["server_port"]

def subdb_downloader(unique_id,lazy_file_hash):
    subdb_filename=unique_id + "_" + lazy_file_hash + ".db"
    if os.path.exists(os.path.join(SUB_DB_PATH,subdb_filename)):
        log(f"{subdb_filename} already exists")
        log(f"Using pre existing subdb. If the node has updated its content and you want that then you need to delete the file {os.path.abspath(os.path.join(SUB_DB_PATH,subdb_filename))}",1)
        return subdb_filename
    if not os.path.exists(SUB_DB_PATH):
        os.makedirs(SUB_DB_PATH)
    ip = get_ip_address(SERVER_ADDR)
    log(f"Connecting to {ip} for subdb_download")
    try:
        # Connect to server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(30)
            s.connect((ip, PORT))
            log("Connected to server")
            js_data = {}
            js_data["subdb_download"] = True
            js_data["unique_id"] = unique_id
            js_data["lazy_file_hash"] = lazy_file_hash
            data_to_send = json.dumps(js_data).encode()
            data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>" #"<"+ sha256 of "<EOF>"+">"
            s.sendall(data_to_send)

            # Receive data from server
            data=b""
            while True:
                chunk = s.recv(1024*100)
                if not chunk:
                    break
                data += chunk
                if data.endswith(b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"): #"<"+ sha256 of "<EOF>"+">"
                    data = data[:-66]  # Remove termination sequence from the data
                    break
            data = json.loads(data.decode())
            if(data['subdb_success']):
                subdb_filename=data["subdb_filename"]
                subdb_data=data["subdb_data"]
                subdb_data=base64.b64decode(subdb_data)
                with open(os.path.join(SUB_DB_PATH,subdb_filename),"wb") as f:
                    f.write(subdb_data)
                log(f"Subdb downloaded successfully")
                s.close()
                return subdb_filename
            else:
                log(f"Subdb download failed",2)
                log(f"It can be due to node not having the file or server is not updated by node yet",1)
                s.close()
                return False
    except socket.timeout:
        log("Connection timed out",2)
        log("Server is down",2)
        return False
    except ConnectionRefusedError:
        log("Server is down",2)
        return False

if __name__ == '__main__':
    log(subdb_downloader("5e7350ca-5dd7-40df-9ea5-b2ece85bc4da","7e31a3f574a4efed49bd0f3e565ac73d"))
    

