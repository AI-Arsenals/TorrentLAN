import socket
import os
import json


CONFIG_IDENTITY = "configs/identity.json"
OWN_UNIQUE_ID = json.load(open(CONFIG_IDENTITY))["client_id"]
DBS_LOCATION = "./data/.other_clients_db"

PORT = 8889

def request_database(client_unique_id,ip,modified_time):
    modified_time=float(modified_time)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, PORT))
            s.sendall("Send".encode())

            # Receive the file
            file_data = b""
            while True:
                data = s.recv(1024)
                if not data:
                    break
                file_data += data

            # Save the received file data
            with open(os.path.join(DBS_LOCATION, client_unique_id+".db"), 'wb') as file:
                file.write(file_data)
            
            # Change the modified time of the file
            os.utime(os.path.join(DBS_LOCATION, client_unique_id+".db"), (modified_time, modified_time))

            print("Database from ",client_unique_id,"Recieved")
            s.close()

    except ConnectionRefusedError:
        print("Client is not up")

def check_updation(client_unique_id,ip):
    try:
        # Connect to clients
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, PORT))
            s.sendall("Update".encode())
            
            # Receive response from server
            data = s.recv(1024)
            if os.path.exists(os.path.join(DBS_LOCATION,client_unique_id+".db")) and data.decode()==str(os.stat(os.path.join(DBS_LOCATION, client_unique_id+".db")).st_mtime):
                print(f"{client_unique_id} is Up to date")
                s.close()
            else:
                print(f"{client_unique_id} is Not up to date")
                s.close()
                request_database(client_unique_id,ip,data.decode())
    except ConnectionRefusedError:
        print("Client is not up")

if __name__ == '__main__':
    check_updation('5e7350ca-5dd7-40df-9ea5-b2ece85bc4da','localhost')
