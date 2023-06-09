import socket
import threading
import os
import json

HOST = 'localhost'
PORT = 8888

DB_LOCATION = "./data/.db/file_tree.db"

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            if data.decode() == "Update":
                date_modified = os.stat(DB_LOCATION).st_mtime
                conn.sendall(str(date_modified).encode())
            elif data.decode() == "Send":
                with open(DB_LOCATION, 'rb') as file:
                    file_data = file.read()
                conn.sendall(file_data)
            break
        except ConnectionResetError:
            print(f"Connection with {addr} closed")
            break
    conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Listening on {HOST}:{PORT}...")
        while True:
            conn, addr = s.accept()

            # Multi thread
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == '__main__':
    start_server()