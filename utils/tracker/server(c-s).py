import socket
import threading
import os
import json
import base64
import datetime
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from utils.tracker.shared_util.intranet_ips_grabber import get_intranet_ips

HOST = get_intranet_ips()
PORT = 8888

DB_LOCATION = "data/.db"
ID_to_IP = "data/id_to_ip.json"
SERVER_LOGS=".server_log"

def logger_server(message, severity_no=0):
    severities={0:"info",1:"warning",2:"error"}
    severity=severities.get(severity_no,"info")
    print(message)
    try:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = "[{}] [{}] {}\n".format(current_time, severity.upper(), message)
        if not os.path.exists(SERVER_LOGS):
            with open(SERVER_LOGS, "w") as f:
                f.write("")
        with open(SERVER_LOGS, 'a') as file:
            file.write(log_message)

        # print(f"Logged message with severity '{severity}' to file: {self.file_path}")
    except IOError:
        print("Error: Unable to write to file: ",SERVER_LOGS)

def handle_client(conn, addr):
    logger_server("Connected by "+ str(addr))
    data=b""
    while True:
        chunk = conn.recv(1024)
        if not chunk:
            break
        data += chunk
        if data.endswith(b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"): #"<"+ sha256 of "<EOF>"+">"
            data = data[:-66]  # Remove termination sequence from the data
            break

    js_data = json.loads(data.decode())
    logger_server("js data : "+str(js_data))
    ip_reg=js_data.get("ip_reg",False)
    ip_get=js_data.get("ip_get",False)

    if ip_get:
        logger_server("Querying a IP")
        unique_ids = js_data['unique_ids']
        with open(ID_to_IP) as f:
            id_to_ip = json.load(f)
        
        return_js_data={}
        for unique_id in unique_ids:
            ip_and_netmask = id_to_ip.get(unique_id, None)
            return_js_data[unique_id] = ip_and_netmask
        conn.sendall(json.dumps(return_js_data).encode())
        conn.close()

    elif ip_reg:
        logger_server("IP registration")
        unique_id = js_data['unique_id']
        ip = js_data['ip']
        netmask=js_data['netmask']
        if not os.path.exists(ID_to_IP):
            with open(ID_to_IP, 'w') as f:
                json.dump({unique_id: [ip,netmask]}, f)
        else:
            with open(ID_to_IP) as f:
                id_to_ip = json.load(f)
            id_to_ip[unique_id] = [ip,netmask]
            with open(ID_to_IP, 'w') as f:
                json.dump(id_to_ip, f)
    else:
        logger_server("DB update")
        unique_id = js_data['unique_id']
        db_data = base64.b64decode(js_data['db_data'])
        with open(os.path.join(DB_LOCATION, unique_id + ".db"), "wb") as f:
            f.write(db_data)
        conn.close()

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    for host in HOST:
        try:
            s.bind((host, PORT))
            s.listen(250)
            logger_server("Listening on " + host + ":" + str(PORT) + "...")
        except Exception as e:
            logger_server("Error binding to " + host + ": " + str(e))
        else:
            break

    while True:
        conn, addr = s.accept()

        # Multi-thread
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == '__main__':
    start_server()
