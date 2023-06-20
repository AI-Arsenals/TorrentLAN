import socket
import threading
import os
import sys
import base64
import select

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from utils.tracker.shared_util.intranet_ips_grabber import get_intranet_ips
from utils.log.main import log

HOST = 'localhost'
PORT = 8889
NODE_p2p_LOGS=".node_p2p_logs"
DB_LOCATION = "./data/.db/file_tree.db"

def handle_client(conn, addr):
    log(f"Connected by {addr}",file_name=NODE_p2p_LOGS)
    while True:
        try:
            data=b""
            while True:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                data += chunk
                if data.endswith(b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"): #"<"+ sha256 of "<EOF>"+">"
                    data = data[:-66]  # Remove termination sequence from the data
                    break

            if data.decode() == "Update":
                date_modified = os.stat(DB_LOCATION).st_mtime
                data_to_send = str(date_modified).encode()
                data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
                conn.sendall(data_to_send)
            elif data.decode() == "Send":
                with open(DB_LOCATION, 'rb') as file:
                    file_data = file.read()
                data_to_send = (base64.b64encode(file_data)).encode()
                data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
                conn.sendall(data_to_send)
            conn.close()
        except ConnectionResetError:
            log(f"Connection with {addr} closed",severity_no=1,file_name=NODE_p2p_LOGS)
            break

def start_server():
    sockets = []
    for host in HOST:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, PORT))
            s.listen(75)
            sockets.append(s)
            log("Listening on " + host + ":" + str(PORT) + "...",file_name=NODE_p2p_LOGS)
        except Exception as e:
            log("Error binding to " + host + ": " + str(e),severity_no=2,file_name=NODE_p2p_LOGS)
    
    while True:
        readable, _, _ = select.select(sockets, [], [])
        for sock in readable:
            conn, addr = sock.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == '__main__':
    start_server()