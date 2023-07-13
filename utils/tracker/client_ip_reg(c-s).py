"""
This module register the client ip with the pc ip in the server
"""

import socket
import os
import json
import sys
import netifaces

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from utils.log.main import log

CONFIG_IDENTITY = "configs/identity.json"
CONFIG_CLIENT = "configs/client_ip_reg(c-s).json"
OWN_UNIQUE_ID = json.load(open(CONFIG_IDENTITY))["client_id"]
SERVER_CONFIG="configs/server.json"
SERVER_ADDR=json.load(open(SERVER_CONFIG))["server_addr"]

PORT = json.load(open(SERVER_CONFIG))["server_port"]

def update_server(unique_id, ip,local_conn_ip,netmask):
    try:
        # Connect to server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            log(f"Connecting to server at {ip}")
            s.timeout(5)
            s.connect((ip, PORT))
            log("Connected to server")
            js_data = {}
            js_data["ip_reg"] = True
            js_data["unique_id"] = unique_id
            js_data["ip"] = local_conn_ip
            js_data["netmask"]=netmask
            data_to_send = json.dumps(js_data).encode()
            data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>" #"<"+ sha256 of "<EOF>"+">"
            s.sendall(data_to_send)
        s.close()
        return True
    except ConnectionRefusedError:
        log("Server is down",2)
        return False

def get_ip_address(address):
    try:
        ip_address = socket.gethostbyname(address)
        return ip_address
    except socket.gaierror:
        log(f"Either server is down, or we are unable to connect to server at {address}",2)
        log(f"By default connecting to local host instead of server at {address}",1)
        return "127.0.0.1"

def get_my_connect_ip(conn_address):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((conn_address, 80))
        local_conn_ip = s.getsockname()[0]
        s.close()
        return local_conn_ip
    except socket.error:
        return None
    
def update(Force_update=False):
    ip = get_ip_address(SERVER_ADDR)
    netmask=get_netmask(ip)
    local_conn_ip = get_my_connect_ip(ip)
    if not os.path.exists(CONFIG_CLIENT):
        with open(CONFIG_CLIENT, 'w') as f:
            json.dump({"local_conn_ip": local_conn_ip}, f)
        success = update_server(OWN_UNIQUE_ID, ip,local_conn_ip,netmask)
        if success:
            log("Successfully updated server")
            with open(CONFIG_CLIENT, 'w') as f:
                json.dump({"Last_Sent": local_conn_ip}, f)
        else:
            os.unlink(CONFIG_CLIENT)
    else:
        with open(CONFIG_CLIENT, 'r') as f:
            data = json.load(f)
            last_local_conn_ip = data.get("local_conn_ip",None)
            if last_local_conn_ip is None or last_local_conn_ip != local_conn_ip or Force_update:
                success = update_server(OWN_UNIQUE_ID, ip,local_conn_ip,netmask)
                if success:
                    log("Successfully updated server")
                    with open(CONFIG_CLIENT, 'w') as f:
                        json.dump({"local_conn_ip": local_conn_ip}, f)
            else:
                log("Already Upto date")

def get_netmask(ip_address):
    # Get the network interfaces
    interfaces = netifaces.interfaces()

    # Iterate over the network interfaces and find the one that matches the provided IP address
    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if socket.AF_INET in addresses:
            for address in addresses[socket.AF_INET]:
                if 'addr' in address and address['addr'] == ip_address:
                    netmask = address.get('netmask')
                    return netmask

    return None

if __name__ == '__main__':
    update()
