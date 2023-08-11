import psutil
import socket
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..')))
from utils.log.main import log

def get_intranet_ips():
    intranet_ips = ['127.0.0.1']

    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ip = addr.address
                mac = addr.address
                # Check for known virtual interfaces
                if mac.startswith(('00:00:00', '08:00:27', '00:1c:42')):
                    continue
                # Check for other conditions if needed
                if mac.startswith('00:'):
                    continue
                # Exclude loopback address and known virtual interfaces
                if ip != '127.0.0.1':
                    intranet_ips.append(ip)

    print(f"Listening at following IPs: {intranet_ips}")
    return intranet_ips

if __name__ == '__main__':
    log(get_intranet_ips())
