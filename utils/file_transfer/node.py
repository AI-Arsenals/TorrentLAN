import time
import socket
import threading
import os
import json
import base64
import sqlite3
import sys
import select
import psutil
from sqlalchemy import text as sanitize


sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..')))
from utils.log.main import log
from utils.tracker.shared_util.intranet_ips_grabber import get_intranet_ips

LIVE_IP_CHECK_CONFIG= "configs/live_ip_check_config.json"
SPEED_TEST_DATA_SIZE = json.load(open(LIVE_IP_CHECK_CONFIG))["speed_test_data_size"]
FILE_TRANSFER_NODE_CONFIG ="configs/file_transfer_node_config.json"


HOST = get_intranet_ips()
NODE_CONFIG='configs/node.json'
PORT = json.load(open(NODE_CONFIG))["port"]

DATABASE_DIR = "data/.db"
NODE_file_transfer_log=".node_file_transfer_log"
CONFIG_FOLDER_LOCATION = "configs/folder_locations.json"
CONFIG_IDENTITY = "configs/identity.json"
OWN_UNIQUE_ID = json.load(open(CONFIG_IDENTITY))["client_id"]

HASH_TO_FILE_DIR_CACHE={}

def handle_client(conn, addr):
    log(f"Connection from {addr}",file_name=NODE_file_transfer_log)
    data = conn.recv(1024)
    # "<"+ sha256 of "<EOF>"+">"
    if data.endswith(b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"):
        data = data[:-66]  # Remove termination sequence from the data
    else:
        log(f"Termination sequence not found in data from {addr}",severity_no=1,file_name=NODE_file_transfer_log)
        conn.close()
        return

    js_data = json.loads(data.decode())
    log(f"Received data from {addr}: {str(js_data)}",file_name=NODE_file_transfer_log)
    live_ip_check= js_data.get("live_ip_check", False)
    file_download = js_data.get("file_download", False)
    ping=js_data.get("ping",False)

    if ping:
        return_js_data = {"ping": True}
        data_to_send = json.dumps(return_js_data).encode()
        data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
        conn.sendall(data_to_send)
        conn.close()

    elif live_ip_check:
        unique_id_check_request = js_data["unique_id"]
        if (unique_id_check_request == OWN_UNIQUE_ID):
            return_js_data = {}
            return_js_data["check_result"] = True
            return_js_data["speed_test_data"]=str(b"0"*SPEED_TEST_DATA_SIZE)
            data_to_send = json.dumps(return_js_data).encode()
            # "<"+ sha256 of "<EOF>"+">"
            data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
            conn.sendall(data_to_send)
        else:
            return_js_data = {"check_result": False}
            data_to_send = json.dumps(return_js_data).encode()
            data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
            conn.sendall(data_to_send)
            log(f"Sent data to {addr}: {str(return_js_data)}",file_name=NODE_file_transfer_log)
        conn.close()
    
    elif file_download:
        start_time = time.time()
        hash = js_data["hash"]
        table_name = js_data["table_name"]
        start_byte = js_data["start_byte"]
        end_byte = js_data["end_byte"]

        data_to_send = {}
        data_to_send["found"] = False

        try :
            found_in_db=False
            hash_in_cache=False
            if hash in HASH_TO_FILE_DIR_CACHE:
                hash_in_cache=True
            if not hash_in_cache:
                with open(CONFIG_FOLDER_LOCATION) as f:
                    table_names = json.load(f).keys()
                if table_name not in table_names:
                    log(f"Table name {table_name} not found in folder_locations.json",severity_no=1,file_name=NODE_file_transfer_log)
                    data_to_send = json.dumps(data_to_send).encode()
                    data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
                    conn.send(data_to_send)
                    conn.close()
                    return
                db_con=sqlite3.connect(os.path.join(DATABASE_DIR,"file_tree.db"))
                cursor=db_con.cursor()
                cursor.execute(f"SELECT * FROM {table_name} WHERE hash = '{sanitize(hash)}'")
                data=cursor.fetchone()
                is_file=data[2]
                if data and is_file:
                    meta_data=json.loads(data[5])
                    file_dir=meta_data["Path"]
                    found_in_db=True
                    HASH_TO_FILE_DIR_CACHE[hash]=file_dir
                    if start_byte and end_byte:
                        with open(file_dir, "rb") as file:
                            file.seek(start_byte)
                            data = file.read(end_byte - start_byte + 1)
                            b64_data = base64.b64encode(data)
                    else:
                        b64_data = base64.b64encode(open(file_dir, "rb").read())
                    data_to_send["found"] = True
                    data_to_send["file_data"] = b64_data.decode()
            elif found_in_db or hash_in_cache:
                file_dir=HASH_TO_FILE_DIR_CACHE[hash]
                if start_byte and end_byte:
                        with open(file_dir, "rb") as file:
                            file.seek(start_byte)
                            data = file.read(end_byte - start_byte + 1)
                            b64_data = base64.b64encode(data)
                else:
                    b64_data = base64.b64encode(open(file_dir, "rb").read())
                data_to_send["found"] = True
                data_to_send["file_data"] = b64_data.decode()
            
            data_to_send = json.dumps(data_to_send).encode()
            data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
            log(f"Data Prepared in {time.time()-start_time} seconds",file_name=NODE_file_transfer_log)
            conn.send(data_to_send)
            log(f"Data Prepared and sent in {time.time()-start_time} seconds",file_name=NODE_file_transfer_log)
            log(f"Sent data to {addr}: {str(file_dir)}",file_name=NODE_file_transfer_log)
        except Exception as e:
            log(f"Error while fetching data from database: {e}",severity_no=1,file_name=NODE_file_transfer_log)
            data_to_send=json.dumps(data_to_send).encode()
            data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
            log(f"Above Error ,Sent data to {addr} : {data_to_send}",severity_no=2,file_name=NODE_file_transfer_log)
            conn.sendall(data_to_send)

        conn.close()


def start_server():
    current_pid=os.getpid()

    if os.path.exists(FILE_TRANSFER_NODE_CONFIG):
        last_hosts=json.loads(open(FILE_TRANSFER_NODE_CONFIG).read())["last_hosts"]
        if last_hosts==HOST:
            EXISTING_PROCESS=False
            for proc in psutil.process_iter():
                try:
                    if (proc.pid != current_pid) and ((("python" in proc.name()))or("python3" in proc.name())) and "utils/file_transfer/node.py" in proc.cmdline():
                        EXISTING_PROCESS=True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            if EXISTING_PROCESS:
                log("Server already running with no network adapter ip changes")
                return
        else:
            open(FILE_TRANSFER_NODE_CONFIG,"w").write(json.dumps({"last_hosts":HOST}))

    if not os.path.exists(FILE_TRANSFER_NODE_CONFIG):
        open(FILE_TRANSFER_NODE_CONFIG,"w").write(json.dumps({"last_hosts":HOST}))

    # Check if the node is already running and terminate it
    for proc in psutil.process_iter():
        try:
            if (proc.pid != current_pid) and (("python" in proc.name())or("python3" in proc.name())) and "utils/file_transfer/node.py" in proc.cmdline():
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    sockets = []
    for host in HOST:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, PORT))
            s.listen(25)
            sockets.append(s)
            log("Listening on " + host + ":" + str(PORT) + "...",file_name=NODE_file_transfer_log)
        except Exception as e:
            log("Error binding to " + host + ": " + str(e),severity_no=2,file_name=NODE_file_transfer_log)
    
    while True:
        readable, _, _ = select.select(sockets, [], [])
        for sock in readable:
            conn, addr = sock.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == '__main__':
    start_server()
