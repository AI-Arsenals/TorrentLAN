import subprocess
import os

TORRENT_LAN_DIR=os.getcwd()

if not os.path.basename(os.path.dirname(__file__))=="TorrentLAN":
    if os.name == 'nt':
        TORRENT_LAN_DIR=os.path.join(os.path.expanduser("~" + os.getlogin()+'/')+"AppData","Local","TorrentLan")
    elif os.name=='posix':
        TORRENT_LAN_DIR=os.path.join(os.path.expanduser("~" + os.getlogin()+'/')+".local", "TorrentLAN")
    elif os.name=='mac':
        TORRENT_LAN_DIR=os.path.expanduser("~" + os.getlogin())

print(f"Starting Django and Electron in {TORRENT_LAN_DIR}")

# Start the Django server
django_process = subprocess.Popen(["python", "./django_for_frontend/manage.py", "runserver"],cwd=TORRENT_LAN_DIR)

if os.name == 'nt':
    # Start the Electron
    frontend_process = subprocess.Popen(["../my-app/dist/win-unpacked/my-app.exe"],cwd=TORRENT_LAN_DIR)
elif os.name=='posix':
    # Start the Electron
    frontend_process = subprocess.Popen(["../my-app/dist/linux-unpacked/my-app"],cwd=TORRENT_LAN_DIR)
elif os.name=='mac':
    # Start the Electron
    frontend_process = subprocess.Popen(["../my-app/dist/mac-unpacked/my-app.app"],cwd=TORRENT_LAN_DIR)


# Wait for processes to complete
django_process.wait()
frontend_process.wait()

print("Both processes have completed.")