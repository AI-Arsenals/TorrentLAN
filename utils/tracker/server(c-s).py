import socket
import threading
import os
import json
import base64

HOST = ''
PORT = 8888

DB_LOCATION = "data/.db"
ID_to_IP = "data/id_to_ip.json"

def handle_client(conn, addr):
    print("Connected by", addr)
    data=b""
    while True:
        chunk = conn.recv(1024)
        if not chunk:
            break
        data += chunk

    js_data = json.loads(data.decode())
    ip_reg=js_data.get("ip_reg",False)
    if ip_reg:
        print("IP registration")
        unique_id = js_data['unique_id']
        ip = js_data['ip']
        if not os.path.exists(ID_to_IP):
            with open(ID_to_IP, 'w') as f:
                json.dump({unique_id: ip}, f)
        else:
            with open(ID_to_IP) as f:
                id_to_ip = json.load(f)
            id_to_ip[unique_id] = ip
            with open(ID_to_IP, 'w') as f:
                json.dump(id_to_ip, f)
    else:
        print("DB update")
        unique_id = js_data['unique_id']
        db_data = base64.b64decode(js_data['db_data'])
        with open(os.path.join(DB_LOCATION, unique_id + ".db"), "wb") as f:
            f.write(db_data)
        conn.close()

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(250)
    print("Listening on", HOST + ":" + str(PORT) + "...")
    while True:
        conn, addr = s.accept()

        # Multi thread
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == '__main__':
    start_server()
