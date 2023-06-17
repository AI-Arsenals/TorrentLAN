import socket
import threading
import os
import json
import sys

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..')))
from utils.log.main import log

HOST = ''
PORT = 8890

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
    unique_id_check_request = js_data.get("unique_id", False)
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
