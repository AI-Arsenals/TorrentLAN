import netifaces
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..')))
from utils.log.main import log

def get_intranet_ips():
    intranet_ips = ["127.0.0.1"]
    interfaces = netifaces.interfaces()

    for interface in interfaces:
        try:
            iface_type = netifaces.ifaddresses(interface).get(netifaces.AF_LINK)
            if iface_type:
                if iface_type[0]['addr'].startswith('00:00:00'):  # Ignore virtual interfaces
                    continue
                if iface_type[0]['addr'].startswith('08:00:27'):  # Ignore VirtualBox interfaces
                    continue
                if iface_type[0]['addr'].startswith('00:1c:42'):  # Ignore VMware interfaces
                    continue

                if iface_type[0]['addr'].startswith('00:'):
                    continue

            addresses = netifaces.ifaddresses(interface)
            ipv4_addresses = addresses.get(netifaces.AF_INET)
            if ipv4_addresses:
                for entry in ipv4_addresses:
                    ip = entry.get('addr')
                    if ip and not ip.startswith('127.'):
                        intranet_ips.append(ip)
        except (KeyError, ValueError):
            pass
    
    log(f"Listening at following IPS: {intranet_ips}")
    return intranet_ips

if __name__ == '__main__':
    log(get_intranet_ips())
