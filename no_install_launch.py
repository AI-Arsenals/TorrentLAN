import subprocess
import os

# Start the Django server
django_process = subprocess.Popen(["start", "/MIN", "cmd", "/k", "python", "./django_for_frontend/manage.py", "runserver"], shell=True)

# Start node
node_process = subprocess.Popen(["start", "/MIN", "cmd", "/k", "python", "./utils/file_transfer/node.py"], shell=True)

# Start the electron
frontend_process = subprocess.Popen(["start", "/MIN", "cmd", "/k", "npm", "run", "dev"], cwd=os.path.join(os.getcwd(),'my-app'), shell=True)