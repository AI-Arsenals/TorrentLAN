# Updated to work with python 2
import socket
import threading
import os
import json

HOST = ''
PORT = 8293

DB_LOCATION = "./data/.db"

def handle_client(conn, addr):
    print ("Connected by", addr)
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            js_data=data.decode()
            unique_id=js_data["unique_id"]
            db_data=js_data["db_data"]
            with open(os.path.join(DB_LOCATION,unique_id+".db"),"wb") as f:
                f.write(db_data)
        except socket.error:
            print ("Connection with", addr, "closed")
            break
    conn.close()

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(250)
    print ("Listening on", HOST + ":" + str(PORT) + "...")
    while True:
        conn, addr = s.accept()

        # Multi thread
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == '__main__':
    start_server()
