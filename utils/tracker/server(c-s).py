import socket
import select
import os
import json
import base64
import threading
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from utils.tracker.shared_util.intranet_ips_grabber import get_intranet_ips
from utils.db_manage.hash_searcher import hash_list_searcher
from utils.db_manage.subdb_maker_with_node import subdb_maker
from utils.db_manage.get_childs import childs
from utils.log.main import log

HOST = get_intranet_ips()
SERVER_CONFIG="data/server.json"
SERVER_CONFIG="configs/server.json"
PORT=json.load(open(SERVER_CONFIG))["server_port"]

DB_LOCATION = "data/.db"
ID_to_IP = "data/id_to_ip.json"
SERVER_LOGS=".server_log"
SUB_DB_PATH = "data/.db/sub_db"

def handle_client(conn, addr):
    log(f"Connected by {addr}",file_name=SERVER_LOGS)
    data=b""
    while True:
        chunk = conn.recv(1024*100)
        if not chunk:
            break
        data += chunk
        if data.endswith(b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"): #"<"+ sha256 of "<EOF>"+">"
            data = data[:-66]  # Remove termination sequence from the data
            break

    js_data = json.loads(data.decode())
    log(f"js_data: {js_data}",severity_no=-1,file_name=SERVER_LOGS)
    ip_reg=js_data.get("ip_reg",False)
    ip_get=js_data.get("ip_get",False)
    db_update=js_data.get("db_update",False)
    hash_to_id=js_data.get("hash_to_id",False)
    subdb_download=js_data.get("subdb_download",False)
    fetch_childs=js_data.get("fetch_childs",False)

    if ip_get:
        log(f"Querying a IP",file_name=SERVER_LOGS)
        unique_ids = js_data['unique_ids']
        with open(ID_to_IP) as f:
            id_to_ip = json.load(f)
        
        return_js_data={}
        for unique_id in unique_ids:
            ip_and_netmask = id_to_ip.get(unique_id, None)
            return_js_data[unique_id] = ip_and_netmask
        data_to_send=json.dumps(return_js_data).encode()
        data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
        conn.sendall(data_to_send)
        log(f"Sending back: {return_js_data}",severity_no=1,file_name=SERVER_LOGS)
        conn.close()
    
    elif fetch_childs:
        log(f"Fetching childs",file_name=SERVER_LOGS)
        unique_id = js_data['unique_id']
        lazy_file_hash = js_data['lazy_file_hash']
        files,folders= childs(unique_id,lazy_file_hash)
        data_to_send={}
        data_to_send['files']=files
        data_to_send['folders']=folders
        data_to_send=json.dumps(data_to_send).encode()
        data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
        conn.sendall(data_to_send)
        log(f"Sending back: {data_to_send}",severity_no=1,file_name=SERVER_LOGS)
        conn.close()
        
    elif ip_reg:
        log("IP registration",file_name=SERVER_LOGS)
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
    elif db_update:
        log("DB update",file_name=SERVER_LOGS)
        unique_id = js_data['unique_id']
        db_data = base64.b64decode(js_data['db_data'])
        with open(os.path.join(DB_LOCATION, unique_id + ".db"), "wb") as f:
            f.write(db_data)
        conn.close()

    elif hash_to_id:
        log("Hash to UNIQUE ID",file_name=SERVER_LOGS)
        hashes = js_data['hashes']
        data_to_send = hash_list_searcher(hashes)
        data_to_send = json.dumps(data_to_send).encode()
        data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
        conn.sendall(data_to_send)
        log(f"Sending back: {data_to_send}",severity_no=1,file_name=SERVER_LOGS)
        conn.close()
        
    elif subdb_download:
        log("SubDB download",file_name=SERVER_LOGS)
        unique_id = js_data['unique_id']
        lazy_file_hash = js_data['lazy_file_hash']
        subdb_filename=unique_id + "_" + lazy_file_hash + ".db"
        data_to_send={}
        data_to_send['subdb_success']=False
        data_to_send['subdb_filename']=subdb_filename
        if subdb_maker(unique_id,lazy_file_hash,subdb_filename):
            data_to_send['subdb_success']=True
            with open(os.path.join(SUB_DB_PATH, subdb_filename), "rb") as f:
                subdb_data = f.read()
            # We can daily remove the subdb for files to be cache but currently instantly removing after sending subdb
            os.remove(os.path.join(SUB_DB_PATH, subdb_filename))
            subdb_data = base64.b64encode(subdb_data)
            data_to_send['subdb_data']=subdb_data.decode()
        else:
            log("SubDB download failed",severity_no=2,file_name=SERVER_LOGS)
        data_to_send = json.dumps(data_to_send).encode()
        data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>" #"<"+ sha256 of "<EOF>"+">"
        conn.sendall(data_to_send)
        conn.close()
    else:
        log("Unknown request",severity_no=2,file_name=SERVER_LOGS)
        conn.close()

def start_server():
    sockets = []
    for host in HOST:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, PORT))
            s.listen(250)
            sockets.append(s)
            log("Listening on " + host + ":" + str(PORT) + "...",file_name=SERVER_LOGS)
        except Exception as e:
            log("Error binding to " + host + ": " + str(e),severity_no=2,file_name=SERVER_LOGS)
    
    while True:
        readable, _, _ = select.select(sockets, [], [])
        for sock in readable:
            conn, addr = sock.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == '__main__':
    start_server()
