import paramiko
import getpass

# The below function is particularly for IITJ
def server_connector_ssh(ldap_username, ldap_password,command_to_exec):
    # SSH server details
    ssh_server = 'home.iitj.ac.in'
    ssh_port = 22
    ssh_username = ldap_username
    ssh_password = ldap_password

    try:
        # Establish SSH connection via VPN
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ssh_server, port=ssh_port, username=ssh_username, password=ssh_password)
        print("SSH connection established successfully.")

        print("To exit the program, enter 'exit'")
        command_to_execute = command_to_exec
        while command_to_execute != 'exit':
            command_to_execute = input("Enter command: ")
            stdin, stdout, stderr = ssh_client.exec_command(command_to_execute)
            output = stdout.read().decode()
            print(output)

        # Close the SSH connection
        ssh_client.close()
        print("SSH connection closed.")

    except paramiko.AuthenticationException:
        print("Authentication failed. Incorrect credentials.")
    except paramiko.SSHException as e:
        print("SSH connection failed:", str(e))

if __name__ == "__main__":
    ldap_username = input("Enter LDAP username: ")
    ldap_password = getpass.getpass("Enter password: ")
    server_connector_ssh(ldap_username, ldap_password,command_to_exec)
