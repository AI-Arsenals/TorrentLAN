"""
This module register the client ip with the pc ip in the server
"""

import socket
import os
import json
import base64

CONFIG_IDENTITY = "configs/identity.json"
CONFIG_CLIENT = "configs/client_ip_reg(c-s).json"
OWN_UNIQUE_ID = json.load(open(CONFIG_IDENTITY))["client_id"]

PORT = 8888

def update_server(unique_id, ip,local_conn_ip):
    try:
        # Connect to server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("Connecting to server")
            s.connect((ip, PORT))
            print("Connected to server")
            js_data = {}
            js_data["ip_reg"] = True
            js_data["unique_id"] = unique_id
            js_data["ip"] = local_conn_ip
            data_to_send = json.dumps(js_data)
            data_to_send += "<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>" #"<"+ sha256 of "<EOF>"+">"
            s.sendall(data_to_send.encode())
        s.close()
        return True
    except ConnectionRefusedError:
        print("Server is down")
        return False

def get_ip_address(address):
    try:
        ip_address = socket.gethostbyname(address)
        return ip_address
    except socket.gaierror:
        return None

def get_my_connect_ip(conn_address):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((conn_address, 80))
        local_conn_ip = s.getsockname()[0]
        s.close()
        return local_conn_ip
    except socket.error:
        return None
    
def update(ip):
    local_conn_ip = get_my_connect_ip(ip)
    if not os.path.exists(CONFIG_CLIENT):
        with open(CONFIG_CLIENT, 'w') as f:
            json.dump({"local_conn_ip": local_conn_ip}, f)
        success = update_server(OWN_UNIQUE_ID, ip,local_conn_ip)
        if success:
            print("Successfully updated server")
            with open(CONFIG_CLIENT, 'w') as f:
                json.dump({"Last_Sent": local_conn_ip}, f)
        else:
            os.unlink(CONFIG_CLIENT)
    else:
        with open(CONFIG_CLIENT, 'r') as f:
            data = json.load(f)
            last_local_conn_ip = data.get("local_conn_ip",None)
            if last_local_conn_ip is None or last_local_conn_ip != local_conn_ip:
                success = update_server(OWN_UNIQUE_ID, ip,local_conn_ip)
                if success:
                    print("Successfully updated server")
                    with open(CONFIG_CLIENT, 'w') as f:
                        json.dump({"local_conn_ip": local_conn_ip}, f)
            else:
                print("Already Upto date")
if __name__ == '__main__':
    ip = get_ip_address('home.iitj.ac.in')
    print(f"Connecting to {ip}")
    update(ip)
