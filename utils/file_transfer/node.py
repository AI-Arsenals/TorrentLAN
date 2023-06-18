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


HOST = ''
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
            json_data = {"check_result": True}
            data_to_send = json.dumps(json_data)
            # "<"+ sha256 of "<EOF>"+">"
            data_to_send += "<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
            conn.sendall(data_to_send.encode())
            log(f"Sent data to {addr}: {str(json_data)}")
        else:
            json_data = {"check_result": False}
            data_to_send = json.dumps(json_data)
            data_to_send += "<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
            conn.sendall(data_to_send.encode())
            log(f"Sent data to {addr}: {str(json_data)}")
        conn.close()
    
    elif file_download:
        hash = js_data["hash"]
        table_name = js_data["table_name"]

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
    s.bind((HOST, PORT))
    s.listen(15)
    log(f"Server started on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()

        # Multi thread
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == '__main__':
    start_server()
