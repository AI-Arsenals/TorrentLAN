import os
import platform
import sys
import time
import base64
import subprocess

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..')))
from utils.log.main import log

def create_symlink(source_path, dest_dir):
    source_path = os.path.realpath(source_path)
    source_name = os.path.split(source_path)[-1]
    dest_path = os.path.realpath(dest_dir + os.sep + source_name)
    source_path = os.path.realpath(source_path)
    dest_path = os.path.realpath(dest_path)
    log(f'source_path: {source_path}, dest_path: {dest_path}')
    try:
        if platform.system() == "Windows":
            import ctypes
            def window_is_admin():
                try:
                    return ctypes.windll.shell32.IsUserAnAdmin()
                except:
                    return False
            if not window_is_admin():
                # Re-launch the script with administrative privileges
                log(f"Please allow the permission to add the file")
                torrent_lan_path = os.path.realpath(__file__).split(os.sep)[:-3]
                torrent_lan_path = os.sep.join(torrent_lan_path)
                encoded_source_path = base64.b64encode(source_path.encode()).decode()
                encoded_dest_dir = base64.b64encode(dest_dir.encode()).decode()
                args = f'{encoded_source_path} {encoded_dest_dir}'  # No quotation marks needed

                # Build the command to run with elevated privileges
                command = [
                    "powershell",
                    "-Command",
                    f'Set-Location -Path "{torrent_lan_path}"; Start-Process python -ArgumentList "{__file__} {args}" -Verb RunAs'
                ]

                # Execute the command with elevated privileges
                output = subprocess.check_output(command, cwd=torrent_lan_path, shell=True, stderr=subprocess.STDOUT)
                output = output.decode(sys.getdefaultencoding())  # Convert bytes to string if needed

                for i in range(1, 5):
                    time.sleep(1)
                    if os.path.exists(dest_path):
                        return True
                return False

        os.symlink(source_path, dest_path)
        log(f"Symlink created successfully from {source_path} to {dest_path}")
    except OSError as e:
        log(f"Failed to create symbolic link: {e}", 2)

if __name__ == "__main__":
    log(f'Arguments: {sys.argv}, len is {len(sys.argv)}')
    if len(sys.argv) == 3:
        log(f'args_decoded args: {os.path.realpath(base64.b64decode(sys.argv[1]).decode())}, {os.path.realpath(base64.b64decode(sys.argv[2]).decode())}')
        create_symlink(os.path.realpath(base64.b64decode(sys.argv[1]).decode()), os.path.realpath(base64.b64decode(sys.argv[2]).decode()))
