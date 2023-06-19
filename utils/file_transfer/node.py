import socket
import threading
import os
import json
import base64
import sqlite3
import sys


sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..')))
from utils.log.main import log
from utils.tracker.shared_util.intranet_ips_grabber import get_intranet_ips

LIVE_IP_CHECK_CONFIG= "configs/live_ip_check_config.json"
SPEED_TEST_DATA_SIZE = json.load(open(LIVE_IP_CHECK_CONFIG))["speed_test_data_size"]


HOST = get_intranet_ips()
PORT = 8890

DATABASE_DIR = "data/.db"
CONFIG_FOLDER_LOCATION = "configs/folder_locations.json"
CONFIG_IDENTITY = "configs/identity.json"
OWN_UNIQUE_ID = json.load(open(CONFIG_IDENTITY))["client_id"]


def handle_client(conn, addr):
    log(f"Connection from {addr}")
    data = conn.recv(1024)
    # "<"+ sha256 of "<EOF>"+">"
    if data.endswith(b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"):
        data = data[:-66]  # Remove termination sequence from the data
    else:
        log(f"Termination sequence not found in data from {addr}")
        conn.close()
        return

    js_data = json.loads(data.decode())
    log(f"Received data from {addr}: {str(js_data)}")
    live_ip_check= js_data.get("live_ip_check", False)
    file_download = js_data.get("file_download", False)
    if live_ip_check:
        unique_id_check_request = js_data["unique_id"]
        if (unique_id_check_request == OWN_UNIQUE_ID):
            return_js_data = {}
            return_js_data["check_result"] = True
            return_js_data["speed_test_data"]=str(b"0"*SPEED_TEST_DATA_SIZE)
            data_to_send = json.dumps(return_js_data)
            # "<"+ sha256 of "<EOF>"+">"
            data_to_send += "<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
            conn.sendall(data_to_send.encode())
        else:
            return_js_data = {"check_result": False}
            data_to_send = json.dumps(return_js_data)
            data_to_send += "<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
            conn.sendall(data_to_send.encode())
            log(f"Sent data to {addr}: {str(return_js_data)}")
        conn.close()
    
    elif file_download:
        hash = js_data["hash"]
        table_name = js_data["table_name"]
        start_byte = js_data["start_byte"]
        end_byte = js_data["end_byte"]

        data_to_send = {}
        data_to_send["found"] = False
        # Find file path in file_tree.db
        with open(CONFIG_FOLDER_LOCATION) as f:
            data = json.load(f)

        try :
            db_con=sqlite3.connect(os.path.join(DATABASE_DIR,"file_tree.db"))
            cursor=db_con.cursor()
            cursor.execute(f"SELECT * FROM {table_name} WHERE hash = '{hash}'")
            data=cursor.fetchone()
            is_file=data[2]
            if data and is_file:
                meta_data=json.loads(data[5])
                file_dir=meta_data["Path"]
                if start_byte and end_byte:
                        with open(file_dir, "rb") as file:
                            file.seek(start_byte)
                            data = file.read(end_byte - start_byte + 1)
                            b64_data = base64.b64encode(data)
                else:
                    b64_data = base64.b64encode(open(file_dir, "rb").read())
                data_to_send["found"] = True
                data_to_send["file_data"] = b64_data.decode()
            
            data_to_send = json.dumps(data_to_send)
            data_to_send += "<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
            conn.sendall(data_to_send.encode())
            log(f"Sent data to {addr}: {str(file_dir)}")
        except Exception as e:
            log(f"Error while fetching data from database: {e}")
            data_to_send = json.dumps(data_to_send)
            data_to_send += "<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
            conn.sendall(json.dumps(data_to_send).encode())

        conn.close()


def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    for host in HOST:
        try:
            s.bind((host, PORT))
            s.listen(250)
            log("Listening on " + host + ":" + str(PORT) + "...")
        except Exception as e:
            log("Error binding to " + host + ": " + str(e))
        else:
            break

    while True:
        conn, addr = s.accept()

        # Multi-thread
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == '__main__':
    start_server()
