# Updated to work with python 2
import socket
import threading
import os
import json

HOST = ''
PORT = 8888

DB_LOCATION = "./data/.db"

def handle_client(conn, addr):
    print ("Connected by", addr)
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            if data == "Update":
                js_data={}
                for i in os.listdir(DB_LOCATION):
                    js_data[i]=os.stat(os.path.join(DB_LOCATION,i)).st_mtime
                conn.sendall(str(js_data))
            elif data == "Send":
                with open(DB_LOCATION, 'rb') as file:
                    file_data = file.read()
                conn.sendall(file_data)
            break
        except socket.error:
            print ("Connection with", addr, "closed")
            break
    conn.close()

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    print "Listening on", HOST + ":" + str(PORT) + "..."
    while True:
        conn, addr = s.accept()

        # Multi thread
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == '__main__':
    start_server()
