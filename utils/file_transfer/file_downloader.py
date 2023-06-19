import socket
import os
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from utils.log.main import log

PORT = 8890

def file_download(ip, hash,table_name,start_byte=None,end_byte=None):
    try:
        # Connect to server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            log(f"Connecting to {ip}:{PORT}")
            s.connect((ip, PORT))
            log(f"Connected")
            js_data = {}
            js_data["file_download"] = True
            js_data["table_name"] = table_name
            js_data["hash"] = hash
            js_data["start_byte"] = start_byte
            js_data["end_byte"] = end_byte
            data_to_send = json.dumps(js_data)
            data_to_send += "<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>" #"<"+ sha256 of "<EOF>"+">"
            s.sendall(data_to_send.encode())
            
            # Receive data
            data=b""
            while True:
                chunk = s.recv(1024)
                if not chunk:
                    break
                data += chunk

            if data.endswith(b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"):
                data = data[:-66]
            else:
                log(f"Termination sequence not found in data from {ip}")
                s.close()
                return False
            return_data = json.loads(data.decode())
            if(return_data["found"]):
                return return_data["file_data"]
            else:
                return False
    except ConnectionRefusedError:
        log(f"The IP {ip} is down", 2)
        return False


if __name__ == '__main__':
    print(file_download("127.0.0.1","fae379b2920b02b4c85110eb4d3f42a9997e669c96b15423f9af8cdfd9775098","Normal_Content_Main_Folder"))
