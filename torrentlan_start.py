import subprocess
import os

TORRENT_LAN_DIR=os.path.abspath(os.getcwd())

if not os.path.basename(os.path.dirname(__file__))=="TorrentLAN":
    if os.name == 'nt':
        TORRENT_LAN_DIR=os.path.join(os.path.expanduser("~" + os.getlogin()+'/')+"AppData","Local","TorrentLan")
    elif os.name=='posix':
        TORRENT_LAN_DIR=os.path.join(os.path.expanduser("~" + os.getlogin()+'/')+".local", "TorrentLAN")
    elif os.name=='mac':
        TORRENT_LAN_DIR=os.path.expanduser("~" + os.getlogin())

print(f"TorrentLAN basedir is at {TORRENT_LAN_DIR}")

# Start the Django server
print(f"Starting django at {os.path.join(TORRENT_LAN_DIR,'django_for_frontend/manage.py')}")
django_python=os.path.join(TORRENT_LAN_DIR,'django_for_frontend/manage.py')
django_process = subprocess.Popen(["python", django_python, "runserver"],cwd=TORRENT_LAN_DIR)

# Start the Electron
if os.name == 'nt':
    print(f"Starting electron at {os.path.join(TORRENT_LAN_DIR,'my-app','dist','win-unpacked','my-app.exe')}")
    electron_executable = os.path.join(TORRENT_LAN_DIR, 'my-app', 'dist', 'win-unpacked', 'my-app.exe')
    frontend_process = subprocess.Popen([electron_executable], cwd=TORRENT_LAN_DIR)
elif os.name=='posix':
    print(f"Starting electron at {os.path.join(TORRENT_LAN_DIR,'my-app','dist','linux-unpacked','my-app')}")
    electron_executable = os.path.join(TORRENT_LAN_DIR, 'my-app', 'dist', 'linux-unpacked', 'my-app')
    frontend_process = subprocess.Popen([electron_executable], cwd=TORRENT_LAN_DIR)
elif os.name=='mac':
    print(f"Starting electron at {os.path.join(TORRENT_LAN_DIR,'my-app','dist','mac-unpacked','my-app.app')}")
    electron_executable = os.path.join(TORRENT_LAN_DIR, 'my-app', 'dist', 'mac-unpacked', 'my-app.app')
    frontend_process = subprocess.Popen([electron_executable], cwd=TORRENT_LAN_DIR)


# Wait for processes to complete
django_process.wait()
frontend_process.wait()

print("Both processes have completed.")