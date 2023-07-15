import os
import platform
import sys
import time
import base64
import subprocess
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils.log.main import log


def create_symlink(source_paths, dest_dir):
    source_paths = [os.path.realpath(source_path) for source_path in source_paths]
    source_names = [os.path.split(source_path)[-1] for source_path in source_paths]
    dest_paths = [os.path.realpath(dest_dir + os.sep + source_name) for source_name in source_names]
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
                log("Please give the permission to add the file")
                torrent_lan_path = os.path.realpath(__file__).split(os.sep)[:-3]
                torrent_lan_path = os.sep.join(torrent_lan_path)
                encoded_source_path = base64.b64encode(json.dumps(source_paths).encode()).decode()
                encoded_dest_dir = base64.b64encode(dest_dir.encode()).decode()
                args = f'{encoded_source_path} {encoded_dest_dir}'  # No quotation marks needed

                # Build the command to run with elevated privileges
                command = [
                    "powershell",
                    "-Command",
                    f'Set-Location -Path "{torrent_lan_path}"; Start-Process python -ArgumentList "{__file__} {args}" -Verb RunAs'
                ]

                # Execute the command with elevated privileges
                subprocess.check_output(command, cwd=torrent_lan_path, shell=True, stderr=subprocess.STDOUT)

                result_arr = [0 for _ in range(len(source_paths))]
                for _ in range(5):  # Check for 5 seconds if the symlink is created or not
                    time.sleep(1)
                    cnt = 0
                    for dest_path in dest_paths:
                        if os.path.exists(dest_path) and not result_arr[dest_paths.index(dest_path)]:
                            cnt += 1
                            result_arr[dest_paths.index(dest_path)] = 1
                        if cnt == len(dest_paths):
                            log(f'Symlink_maker logs -(source_path,dest_path,result_of_symlink_making): {[(source_path,dest_path,bool(result_arr)) for source_path,dest_path,result_arr in zip(source_paths,dest_paths,result_arr)]}')
                            return True, result_arr
                return False, result_arr

        for source_path, dest_path in zip(source_paths, dest_paths):
            try:
                os.symlink(source_path, dest_path)
                log(f"Symlink created successfully from {source_path} to {dest_path}")
            except OSError as e:
                log(f"Failed to create symbolic link: from {source_paths} to {dest_path} with error: {e}", 2)
    except Exception as e:
        log(f"Failed to create symbolic link: from {source_paths} to {dest_dir} with error: {e}", 2)
        return False, [0 for _ in range(len(source_paths))]


if __name__ == "__main__":
    if len(sys.argv) == 3:
        source_paths = json.loads(base64.b64decode(sys.argv[1]).decode())
        dest_dir = base64.b64decode(sys.argv[2]).decode()
        create_symlink(source_paths, dest_dir)
