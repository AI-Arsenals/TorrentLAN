import socket
import os
import json
import subprocess
import platform

CONFIG_IDENTITY = "configs/identity.json"
CONFIG_CLIENT = "configs/client(c-s).json"
OWN_UNIQUE_ID = json.load(open(CONFIG_IDENTITY))["client_id"]
DBS_LOCATION = "./data/.db"+OWN_UNIQUE_ID

PORT = 8293

def update_server(unique_id,ip):
    try:
        # Connect to server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, PORT))
            js_data={}
            js_data[unique_id]=os.stat(DBS_LOCATION).st_mtime
            with open(DBS_LOCATION,"rb") as f:
                js_data["db_data"]=f.read()

    except ConnectionRefusedError:
        print("Server is down")
        return False

def get_ip_address(address):
    try:
        ip_address = socket.gethostbyname(address)
        return ip_address
    except socket.gaierror:
        return None

def check_updation(ip):
    mtime=os.stat(DBS_LOCATION).st_mtime

    if not (os.path.exists(CONFIG_CLIENT)):
        with open(CONFIG_CLIENT, 'w') as f:
            json.dump({"Last_Sent":mtime}, f)
            success=update_server(OWN_UNIQUE_ID,ip)
            if success:
                with open(CONFIG_CLIENT, 'w') as f:
                    json.dump({"Last_Sent":mtime}, f)
            else:   
                os.remove(CONFIG_CLIENT)

    else:
        with open(CONFIG_CLIENT, 'r') as f:
            data=json.load(f)
            if data["Last_Sent"]!=mtime:
                success=update_server(OWN_UNIQUE_ID,ip)
                if success:
                    with open(CONFIG_CLIENT, 'w') as f:
                        json.dump({"Last_Sent":mtime}, f)


if __name__ == '__main__':
    ip=get_ip_address('home.iitj.ac.in')
    # print(ip)
    check_updation(ip)
