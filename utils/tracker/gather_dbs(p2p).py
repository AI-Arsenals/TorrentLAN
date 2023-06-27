import socket
import os
import json
import base64
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from utils.log.main import log

DBS_LOCATION = "./data/.other_clients_db"

PORT = 8889

def request_database(client_unique_id,ip,modified_time):
    modified_time=float(modified_time)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, PORT))
            data_to_send = "Send".encode()
            data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
            s.sendall(data_to_send)

            data=b""
            while True:
                chunk = s.recv(1024*100)
                if not chunk:
                    break
                data += chunk
                if data.endswith(b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"): #"<"+ sha256 of "<EOF>"+">"
                    data = data[:-66]  # Remove termination sequence from the data
                    break

            # Save the received file data
            with open(os.path.join(DBS_LOCATION, client_unique_id+".db"), 'wb') as file:
                file_data=base64.b64decode(data)
                file.write(file_data)
            
            # Change the modified time of the file
            os.utime(os.path.join(DBS_LOCATION, client_unique_id+".db"), (modified_time, modified_time))

            log(f"Database from {client_unique_id} received")
            s.close()

    except ConnectionRefusedError:
        log(f"Client {client_unique_id} is not up", 1)

def check_updation(client_unique_id,ip):
    try:
        # Connect to clients
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, PORT))
            data_to_send="Update".encode()
            data_to_send+=b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"
            s.sendall(data_to_send)
            
            # Receive response from server
            data = s.recv(1024)
            if data.endswith(b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"): #"<"+ sha256 of "<EOF>"+">"
                data = data[:-66]  # Remove termination sequence from the data
            if os.path.exists(os.path.join(DBS_LOCATION,client_unique_id+".db")) and data.decode()==str(os.stat(os.path.join(DBS_LOCATION, client_unique_id+".db")).st_mtime):
                log(f"{client_unique_id} is Up to date")
                s.close()
            else:
                log(f"{client_unique_id} is Not up to date")
                s.close()
                request_database(client_unique_id,ip,data.decode())
    except ConnectionRefusedError:
        log(f"Client {client_unique_id} is not up",1)

if __name__ == '__main__':
    check_updation('5e7350ca-5dd7-40df-9ea5-b2ece85bc4da','localhost')
