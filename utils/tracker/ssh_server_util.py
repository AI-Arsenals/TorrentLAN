import paramiko
import getpass

#The below function is particularly for IITJ
def server_connector__ssh_over_vpn(ldap_username, ldap_password):
    # VPN Gateway details
    vpn_gateway = 'gateway.iitj.ac.in'
    vpn_username = ldap_username
    vpn_password = ldap_password

    # SSH server details
    ssh_server = 'home.iitj.ac.in'
    ssh_port = 22
    ssh_username = ldap_username
    ssh_password = ldap_password

    try:
        # Establish Fortinet VPN connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(vpn_gateway, username=vpn_username, password=vpn_password)
        print("Fortinet VPN connection established successfully.")

        try:
            # Establish SSH connection via VPN
            transport = ssh_client.get_transport()
            dest_addr = (ssh_server, ssh_port)
            local_addr = ('localhost', 0)
            channel = transport.open_channel("direct-tcpip", dest_addr, local_addr)

            # Connect to SSH server through the VPN tunnel
            ssh_tunnel = paramiko.SSHClient()
            ssh_tunnel.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_tunnel.connect(ssh_server, username=ssh_username, password=ssh_password, sock=channel)
            print("SSH connection established successfully.")

            print("To exit the program, enter 'exit'")
            command_to_execute = ''
            while command_to_execute != 'exit':
                command_to_execute = input("Enter command: ")
                stdin, stdout, stderr = ssh_tunnel.exec_command(command_to_execute)
                output = stdout.read().decode()
                print(output)

            # Close the SSH connections
            ssh_tunnel.close()
            ssh_client.close()
            print("SSH connections closed.")

        except paramiko.AuthenticationException:
            print("Authentication failed. Incorrect credentials.")
        except paramiko.SSHException as e:
            print("SSH connection failed:", str(e))

    except paramiko.AuthenticationException:
        print("Fortinet VPN authentication failed. Incorrect credentials.")
    except paramiko.SSHException as e:
        print("Fortinet VPN connection failed:", str(e))

if __name__ == "__main__":
    ldap_username = input("Enter LDAP username: ")
    ldap_password = getpass.getpass("Enter password: ")
    server_connector__ssh_over_vpn(ldap_username, ldap_password)
