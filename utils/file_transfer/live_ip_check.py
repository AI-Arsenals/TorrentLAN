"""
This module contacts unique_id server and check if it is alive and correct
"""

import socket
import os
import json
import time
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from utils.log.main import log

LIVE_IP_CHECK_CONFIG= "configs/live_ip_check_config.json"
SPEED_TEST_DATA_SIZE = json.load(open(LIVE_IP_CHECK_CONFIG))["speed_test_data_size"]

PORT = 8890

import socket

def live_ip_checker(unique_id, ip):
    try:
        # Connect to server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(8) 
            log(f"Connecting to {ip}:{PORT}")
            s.connect((ip, PORT))
            log(f"Connected")

            # Find Ping
            js_data = {}
            js_data["ping"] = True
            data_to_send = json.dumps(js_data).encode()
            data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>" #"<"+ sha256 of "<EOF>"+">"
            s.sendall(data_to_send)
            start_time = time.time()
            data = s.recv(1024)
            if data.endswith(b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"):
                data = data[:-66]
            else:
                log(f"Termination sequence not found in data from {ip}")
                s.close()
                return False
            one_way_ping_time = time.time() - start_time
            s.close()

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(30)
                    s.connect((ip, PORT))
                    # Find transfer speed and check correct unique_id
                    js_data = {}
                    js_data["live_ip_check"] = True
                    js_data["unique_id"] = unique_id
                    data_to_send = json.dumps(js_data).encode()
                    data_to_send += b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>" #"<"+ sha256 of "<EOF>"+">"
                    s.sendall(data_to_send)
                    # Receive data and measure transfer speed
                    start_time = time.time()
                    data = b""
                    while True:
                        chunk = s.recv(1024+SPEED_TEST_DATA_SIZE)
                        if not chunk:
                            break
                        data+=chunk
                    if data.endswith(b"<7a98966fd8ec965d43c9d7d9879e01570b3079cacf9de1735c7f2d511a62061f>"):
                        data = data[:-66]
                    else:
                        log(f"Termination sequence not found in data from {ip}")
                        s.close()
                        return False
                    one_way_end_time = time.time()
                    time_taken=one_way_end_time-start_time-one_way_ping_time
                    return_data = json.loads(data.decode())
                    if not return_data["check_result"]:
                        log(f"Unique ID {unique_id} is not correct for ip {ip}", 1)
                        # report to threat_report module
                        return False
                    # speed_test_data=return_data["speed_test_data"]
                    transfer_speed = len(data) / (time_taken +1e-10)
                s.close()
                return return_data["check_result"],transfer_speed
            except ConnectionRefusedError:
                log(f"The IP {ip} is down", 1)
                return False
            except socket.timeout:
                log(f"Connection to {ip} timed out", 1)
                return False
    except ConnectionRefusedError:
        log(f"The IP {ip} is down", 1)
        return False
    except socket.timeout:
        log(f"Connection to {ip} timed out", 1)
        return False


if __name__ == '__main__':
    log(f"Speed is :{live_ip_checker('5e7350ca-5dd7-40df-9ea5-b2ece85bc4da','127.0.0.1')[1]/10**6} MB/s")
