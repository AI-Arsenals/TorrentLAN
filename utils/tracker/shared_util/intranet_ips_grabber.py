import socket
import netifaces

def get_intranet_ips():
    intranet_ips = ["127.0.0.1"]
    interfaces = netifaces.interfaces()

    for interface in interfaces:
        try:
            addresses = netifaces.ifaddresses(interface)
            ipv4_addresses = addresses.get(netifaces.AF_INET)
            if ipv4_addresses:
                for entry in ipv4_addresses:
                    ip = entry.get('addr')
                    if ip and not ip.startswith('127.'):
                        intranet_ips.append(ip)
        except (KeyError, ValueError):
            pass

    return intranet_ips

if __name__ == '__main__':
    print(get_intranet_ips())