import psutil
import socket
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..')))
from utils.log.main import log

def is_interface_up(interface_name):
    interface = psutil.net_if_stats().get(interface_name)
    return interface is not None and interface.isup

def get_intranet_ips():
    intranet_ips = ['127.0.0.1']

    for interface, addrs in psutil.net_if_addrs().items():
        if is_interface_up(interface):  # Check if the interface is up
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip = addr.address
                    if ip not in intranet_ips:
                        intranet_ips.append(ip)

    print(f"Listening at the following IPs: {intranet_ips}")
    return intranet_ips

if __name__ == '__main__':
    log(get_intranet_ips())
