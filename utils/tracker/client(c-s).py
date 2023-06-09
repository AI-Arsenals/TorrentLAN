import socket
import os
import json
import base64

CONFIG_IDENTITY = "configs/identity.json"
CONFIG_CLIENT = "configs/client(c-s).json"
OWN_UNIQUE_ID = json.load(open(CONFIG_IDENTITY))["client_id"]
DBS_LOCATION = "./data/.db/file_tree.db"

PORT = 8293

def update_server(unique_id, ip):
    try:
        # Connect to server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("Connecting to server")
            s.connect((ip, PORT))
            print("Connected to server")
            js_data = {}
            js_data["unique_id"] = unique_id
            with open(DBS_LOCATION, "rb") as f:
                js_data["db_data"] = base64.b64encode(f.read()).decode()
            data_to_send = json.dumps(js_data)
            s.sendall(data_to_send.encode())
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

def check_updation(ip):
    mtime = os.stat(DBS_LOCATION).st_mtime

    if not os.path.exists(CONFIG_CLIENT):
        with open(CONFIG_CLIENT, 'w') as f:
            json.dump({"Last_Sent": mtime}, f)
        success = update_server(OWN_UNIQUE_ID, ip)
        if success:
            print("Successfully updated server")
            with open(CONFIG_CLIENT, 'w') as f:
                json.dump({"Last_Sent": mtime}, f)
        else:
            os.unlink(CONFIG_CLIENT)
    else:
        with open(CONFIG_CLIENT, 'r') as f:
            data = json.load(f)
            last_sent = data.get("Last_Sent",None)
            if last_sent is None or last_sent != mtime:
                success = update_server(OWN_UNIQUE_ID, ip)
                if success:
                    print("Successfully updated server")
                    with open(CONFIG_CLIENT, 'w') as f:
                        json.dump({"Last_Sent": mtime}, f)
            else:
                print("Already Upto date")
if __name__ == '__main__':
    ip = get_ip_address('home.iitj.ac.in')
    print(f"Connecting to {ip}")
    check_updation(ip)
