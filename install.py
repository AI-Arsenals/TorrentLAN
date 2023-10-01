import subprocess
import os
import sys
import shutil
import platform
import time
import json
import base64

class INSTALL:
    ######### Intitialize variables #########
    if getattr(sys, 'frozen', False):
        TEMP_DIR = os.path.join(sys._MEIPASS)
    else:
        TEMP_DIR=os.getcwd()

    
    if platform.system() == "Windows":
        BASE_DIR = os.path.join(os.environ["LOCALAPPDATA"], "TorrentLAN")
    elif platform.system() == "Linux":
        user_dir = os.path.expanduser("~" + os.getlogin())
        BASE_DIR = os.path.join(user_dir, ".local", "TorrentLAN")
        import getpass
        user= os.getenv("SUDO_USER")
    elif platform.system() == "Darwin":
        user_dir = os.path.expanduser("~" + os.getlogin())
        BASE_DIR = os.path.join(user_dir, "TorrentLAN")
    else:
        print("Unsupported OS")
        sys.exit(1)
    new_install = True


    # Try python3
    result = subprocess.run(['python3', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode()
    if output.startswith('Python') and int(output[7])>=3:
        py = 'python3'
    else:
        # Try python
        result=subprocess.run(['python', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode()
        if output.startswith('Python') and int(output[7])>=3:
            py = 'python'
        else:
            print("Python not found or please install python version 3")
            sys.exit(1)
  
        
    ######### Initalize variables ends #########    
    
    class ALL_PLATFORMS:
        def run_once(file_loc):
            if not INSTALL.new_install:
                return
            # run the file once
            BASE_DIR=INSTALL.BASE_DIR
            command="pythonw " + file_loc
            # Run the command in a new process with a new console window
            if platform.system=='Linux':
                subprocess.run("sudo -u "+INSTALL.user+" "+command, cwd=BASE_DIR, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else :
                subprocess.run(command, cwd=BASE_DIR, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            
        def copy_to_program_files():
            BASE_DIR=INSTALL.BASE_DIR
            TEMP_DIR=INSTALL.TEMP_DIR
            
            if not os.path.exists(BASE_DIR):
                print("Installing TorrentLAN ...")
                print(f"Copying files to {BASE_DIR} from {TEMP_DIR}")
                shutil.copytree(TEMP_DIR, BASE_DIR)

                js_data={"BASE_DIR":BASE_DIR}
                with open(os.path.join(BASE_DIR,"configs/base_dir.json"), 'w') as f:
                    json.dump(js_data, f)
            else:   
                print("Updating TorrentLAN ...")
                print(f"Copying files to {BASE_DIR} from {TEMP_DIR}")
                INSTALL.new_install = False
                # Update all except the 'configs' and 'data' folders
                for root, dirs, files in os.walk(TEMP_DIR):
                    if 'configs' in dirs:
                        dirs.remove('configs')
                    if 'data' in dirs:
                        dirs.remove('data')
                    for file in files:
                        src_path = os.path.join(root, file)
                        dst_path = os.path.join(BASE_DIR, root.replace(TEMP_DIR, '').lstrip('/'), file)
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        shutil.copy(src_path, dst_path)
            if platform.system() == "Linux":  
                # Set the setgid permission
                subprocess.run(["sudo", "setfacl", "-Rm", f"default:user:{INSTALL.user}:rwx,default:group::rwx,default:other::---", BASE_DIR])

                # Change the group ownership of the directory to the current user's group
                subprocess.run(["sudo", "chown", f"{INSTALL.user}:{INSTALL.user}", BASE_DIR])

                # Grant read, write, and execute permissions to the current user and the group
                subprocess.run(["sudo", "chmod", "u+rwx,g+rwx", BASE_DIR])
                def recursive_chmod(path):
                    for root, dirs, files in os.walk(path):
                        for dir in dirs:
                            dir_path = os.path.join(root, dir)
                            os.chmod(dir_path, 0o777)
                        for file in files:
                            file_path = os.path.join(root, file)
                            os.chmod(file_path, 0o777)
                recursive_chmod(BASE_DIR)
                os.chmod(BASE_DIR, 0o777)

                js_data={"BASE_DIR":BASE_DIR}
                with open(os.path.join(BASE_DIR,"configs/base_dir.json"), 'w') as f:
                    json.dump(js_data, f)
                os.chmod(os.path.join(BASE_DIR,"configs/base_dir.json"), 0o777)
            print(f"Copying complete")

    class WINDOWS:
        @staticmethod
        def create_shortcut(source_loc, destination_loc,name,icon_path=None):
            if not INSTALL.new_install:
                return
            if not os.path.exists(destination_loc):
                os.makedirs(destination_loc)
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(os.path.join(destination_loc, name+".lnk"))
            shortcut.Targetpath = source_loc
            if icon_path:
                total_path = os.path.join(INSTALL.BASE_DIR, icon_path)
                shortcut.IconLocation = total_path
            shortcut.save()
            print(f"Created shortcut for {source_loc} at {destination_loc} with name {name}")
            
        @staticmethod
        def daemon_startup(file_loc):
            if not INSTALL.new_install:
                return
            import win32com
            
            BASE_DIR = INSTALL.BASE_DIR
            daemons_folder_path = os.path.join(BASE_DIR,'daemons')
            os.makedirs(daemons_folder_path, exist_ok=True)

            # Create a vbs script to run the daemon script
            vbs_file_path = os.path.join(daemons_folder_path, "TorrentLAN - (Run on Startup) - " + str(file_loc).replace("\\", "_").replace("\\", "_")+".vbs")
            with open(vbs_file_path, 'w') as f:
                f.write('Set objShell = CreateObject("WScript.Shell")\n')
                f.write(f'objShell.CurrentDirectory = "{BASE_DIR}"\n')
                f.write(f'objShell.Run "pythonw {file_loc}", 0, False\n')
                

            # Task Scheduler object
            scheduler = win32com.client.Dispatch("Schedule.Service")
            scheduler.Connect()

            # Get root folder of the Task Scheduler
            root_folder = scheduler.GetFolder("\\")

            # Create a new folder for TorrentLAN if it doesn't exist
            daemon_folder_name = "TorrentLAN"
            daemon_folder_path = "\\" + daemon_folder_name
            try:
                daemon_folder = root_folder.GetFolder(daemon_folder_path)
            except:
                daemon_folder = root_folder.CreateFolder(daemon_folder_path)

            # Task to run on startup
            task_startup = scheduler.NewTask(0)
            task_startup.RegistrationInfo.Description = "TorrentLAN_(Run on Startup)_"
            task_startup.Settings.Enabled = True
            task_startup.Settings.StartWhenAvailable = True

            # Trigger to run on startup
            trigger_startup = task_startup.Triggers.Create(9)  # 9 represents "On startup" trigger
            trigger_startup.Id = "TorrentLAN_(Startup Trigger_" + str(file_loc).replace("\\", "_")

            # Run the vbs file
            action_startup = task_startup.Actions.Create(0)  # 0 represents "Execute" action
            action_startup.Path = "wscript.exe"
            action_startup.Arguments = f'"{vbs_file_path}"'

            # Register the task in the daemon folder
            daemon_folder.RegisterTaskDefinition(str("TorrentLAN - (Daemon - Startup) - " + str(file_loc).replace("\\", "_")),
                                                task_startup, 6, "", "", 3)

            print(f"Created startup daemon for {file_loc}")

        @staticmethod
        def daemon_time(file_loc,recur_time_min):
            if not INSTALL.new_install:
                return
            
            BASE_DIR = INSTALL.BASE_DIR

            daemons_folder_path = os.path.join(BASE_DIR,'daemons')
            os.makedirs(daemons_folder_path, exist_ok=True)
            # Create a vbs script to run the daemon script
            vbs_file_path = os.path.join(daemons_folder_path, "TorrentLAN - (Time Daemon) - " + str(file_loc).replace("\\", "_")+".vbs")
            with open(vbs_file_path, 'w') as f:
                f.write('Set objShell = CreateObject("WScript.Shell")\n')
                f.write(f'objShell.CurrentDirectory = "{BASE_DIR}"\n')
                f.write(f'objShell.Run "pythonw {file_loc}", 0, False\n')

            # Create a scheduled task to run the vbs file every 5 minutes
            task_name = "TorrentLAN - (Time Daemon) - " + str(file_loc).replace("\\",  "_")
            task_command = f'schtasks /create /tn "\\TorrentLAN\\{task_name}" /tr "wscript.exe \\"{vbs_file_path}\\"" /sc minute /mo {recur_time_min} /F'
            subprocess.run(task_command, shell=True)
            
            print(f"Created Time daemon for {file_loc}")

        @staticmethod
        def window_is_admin():
            if os.name == 'nt':
                import ctypes
                import traceback
                try:
                    return ctypes.windll.shell32.IsUserAnAdmin()
                except:
                    traceback.print_exc()
                    print ("Admin check failed, assuming not an admin.")
                    return False
            elif os.name == 'posix':
                # Check for root on Posix
                return os.getuid() == 0

            
        @staticmethod
        def runAsAdmin_windows(args=None,cmdLine=None, wait=True):
            import sys, types
            import win32con, win32event, win32process
            from win32com.shell.shell import ShellExecuteEx
            from win32com.shell import shellcon

            python_exe = sys.executable
            if cmdLine is None:
                cmdLine = [python_exe] + sys.argv+[args]
            elif type(cmdLine) not in (types.TupleType,types.ListType):
                raise ValueError
            cmd = '"%s"' % (cmdLine[0],)
            params = " ".join(['"%s"' % (x,) for x in cmdLine[1:]])
            cmdDir = ''
            showCmd = win32con.SW_SHOWNORMAL
            #showCmd = win32con.SW_HIDE
            lpVerb = 'runas'  # causes UAC elevation prompt.
            procInfo = ShellExecuteEx(nShow=showCmd,
                                    fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                                    lpVerb=lpVerb,
                                    lpFile=cmd,
                                    lpParameters=params)
            if wait:
                procHandle = procInfo['hProcess']    
                obj = win32event.WaitForSingleObject(procHandle, win32event.INFINITE)
                rc = win32process.GetExitCodeProcess(procHandle)
            else:
                rc = None

            return rc

        # # use below as a template for runasadmin_windows
        # def runasadmin_help_windows(args=None):
        #     rc = 0
        #     if not INSTALL.WINDOWS.window_is_admin():
        #         # print ("You're not an admin."), os.getpid(), "params: ", sys.argv
        #         rc = INSTALL.WINDOWS.runAsAdmin_windows(args)
        #     else:
        #         print ("You are an admin!"), os.getpid(), "params: ", sys.argv
        #         rc = 0
        #     x = input('Press Enter to exit.')
        #     return rc

        @staticmethod
        def get_user_directory():
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
                user_directory = winreg.QueryValueEx(key, "Personal")[0]
                winreg.CloseKey(key)

                return os.path.dirname(user_directory)
            except Exception as e:
                print(f"Error: {e}")
                return None

    class LINUX:
        @staticmethod
        def create_shortcut(source_loc, destination_loc, name,icon_path=None):
            if not INSTALL.new_install:
                return
            shortcut_path = os.path.join(destination_loc, name)

            if os.path.exists(shortcut_path):
                print(f"Shortcut already exists at {shortcut_path}")
            else:
                command = f"ln -s '{source_loc}' '{shortcut_path}'"
                if icon_path:
                    total_path = os.path.join(INSTALL.BASE_DIR, icon_path)
                    command += f" -i '{total_path}'"

                subprocess.run(command, shell=True)
                print(f"Created shortcut for {source_loc} at {shortcut_path} with name {name}")


        @staticmethod
        def daemon_startup(file_loc):
            if not INSTALL.new_install:
                return
            import textwrap
                
            BASE_DIR = INSTALL.BASE_DIR

            new_str = str(file_loc).replace("(", "_").replace(")", "_").replace("/", "_").replace("/", "_").replace("-", "_")
            # remove ext
            new_str=new_str.replace(".","")

            daemons_folder_path = os.path.join(BASE_DIR,'daemons')
            os.makedirs(daemons_folder_path, exist_ok=True)
            # Create a shell file to change directory and run the daemon script
            bash_file_path = os.path.join(daemons_folder_path, "TorrentLAN_Startup_" + new_str+".sh")
            with open(bash_file_path, 'w') as f:
                f.write('#!/bin/bash\n')
                f.write(f'cd "{BASE_DIR}"\n')
                f.write(f'sudo -u {INSTALL.user} nohup {INSTALL.py} {file_loc} &')
            os.chmod(bash_file_path, 0o777)

            # Service file content
            service_content = textwrap.dedent(f"""\
            [Unit]
            Description=TorrentLAN - Startup - {new_str} 
            After=network.target

            [Service]
            ExecStart=bash {bash_file_path}
            WorkingDirectory={BASE_DIR}

            [Install]
            WantedBy=default.target
            """)

            daemon_folder_path = os.path.join('/etc/systemd/system')
            os.makedirs(daemon_folder_path, exist_ok=True)

            service_file_path = os.path.join(daemon_folder_path, 'TorrentLAN_Startup' + new_str + '.service')
            with open(service_file_path, 'w') as service_file:
                service_file.write(service_content)

            os.system("systemctl daemon-reload")
            os.system(f'systemctl enable {service_file_path}')

            print(f"Created startup daemon for {file_loc}")

        @staticmethod
        def daemon_networkchange(file_loc):
            if not INSTALL.new_install:
                return
            import textwrap

            BASE_DIR = INSTALL.BASE_DIR
            new_str = str(file_loc).replace("(", "_").replace(")", "_").replace("/", "_").replace("/", "_").replace("-", "_")   
            # remove ext
            new_str=new_str.replace(".","")

             

            daemons_folder_path = os.path.join(BASE_DIR,'daemons')
            os.makedirs(daemons_folder_path, exist_ok=True)
            # Create a shell file to change directory and run the daemon script
            bash_file_path = os.path.join(daemons_folder_path, "TorrentLAN_NetworkChange_" + new_str+".sh")
            with open(bash_file_path, 'w') as f:
                f.write('#!/bin/bash\n')
                f.write(f'cd "{BASE_DIR}"\n')
                f.write(f'sudo -u {INSTALL.user} nohup {INSTALL.py} {file_loc} &')
            os.chmod(bash_file_path, 0o777)

            # Service file content
            service_content = textwrap.dedent(f"""\
            [Unit]
            Description=TorrentLAN - Network Change - {new_str}

            [Service]
            Type=simple
            ExecStart=bash {bash_file_path}
            WorkingDirectory={BASE_DIR}

            [Install]
            WantedBy=network.target
            """)

            daemon_folder_path = os.path.join('/etc/systemd/system')
            os.makedirs(daemon_folder_path, exist_ok=True)

            # Write the service file
            service_file_path = os.path.join(daemon_folder_path, 'TorrentLAN_NetworkChange_' + new_str + '.service')
            with open(service_file_path, 'w') as service_file:
                service_file.write(service_content)

            os.system("systemctl daemon-reload")
            os.system(f"systemctl enable {service_file_path}")

            print(f"Created network change daemon for {file_loc}")
        
        @staticmethod
        def daemon_time(file_loc, recur_time_min):
            if not INSTALL.new_install:
                return
            import textwrap
            
            BASE_DIR = INSTALL.BASE_DIR
            new_str = str(file_loc).replace("(", "_").replace(")", "_").replace("/", "_").replace("/", "_").replace("-", "_")   
            # remove ext
            new_str = new_str.replace(".", "")
            daemons_folder_path = os.path.join(BASE_DIR, 'daemons')
            os.makedirs(daemons_folder_path, exist_ok=True)
            # Create a shell file to change directory and run the daemon script
            bash_file_path = os.path.join(daemons_folder_path, "TorrentLAN_TimeDaemon_" + new_str + ".sh")
            with open(bash_file_path, 'w') as f:
                f.write('#!/bin/bash\n')
                f.write(f'cd "{BASE_DIR}"\n')
                f.write('while true; do\n')
                f.write(f'\tsudo -u {INSTALL.user} {INSTALL.py} {file_loc} &\n')
                f.write(f'\tsleep {int(recur_time_min)*60}\n')
                f.write('done\n')
            os.chmod(bash_file_path, 0o777)

            # Service file content
            service_content = textwrap.dedent(f"""\
            [Unit]
            Description=TorrentLAN - Time Daemon - {new_str}

            [Service]
            Type=simple
            ExecStart=bash {bash_file_path}
            WorkingDirectory={BASE_DIR}

            [Install]
            WantedBy=timers.target
            """)

            daemon_folder_path = os.path.join('/etc/systemd/system')
            os.makedirs(daemon_folder_path, exist_ok=True)

            # Write the service file
            service_file_path = os.path.join(daemon_folder_path, 'TorrentLAN_TimeDaemon_' + new_str + '.service')
            with open(service_file_path, 'w') as service_file:
                service_file.write(service_content)

            os.system("systemctl daemon-reload")
            os.system(f"systemctl enable {service_file_path}")

            timer_content = textwrap.dedent(f"""\
            [Unit]
            Description=TorrentLAN - Time Daemon Timer - {new_str}

            [Timer]
            OnBootSec=1min
            OnUnitActiveSec={recur_time_min}min
            Unit=TorrentLAN_TimeDaemon_{new_str}.service

            [Install]
            WantedBy=timers.target
            """)

            # Write the timer file
            timer_file_path = os.path.join(daemon_folder_path, 'TorrentLAN_TimeDaemon_' + new_str + '.timer')
            with open(timer_file_path, 'w') as timer_file:
                timer_file.write(timer_content)

            subprocess.run(["systemctl", "daemon-reload"], check=True)
            subprocess.run(["systemctl", "enable", os.path.basename(timer_file_path)], check=True)
            subprocess.run(["systemctl", "start", os.path.basename(timer_file_path)], check=True)
                               
            print(f"Created network change daemon for {file_loc} with recur time {recur_time_min} min")

    class MAC:
        @staticmethod
        def create_shortcut(source_loc, destination_loc, name,icon_path=None):
            if not INSTALL.new_install:
                return

            # Create the alias (shortcut)
            alias_path = os.path.join(destination_loc, name + ".alias")

            command=f"ln -s '{source_loc}' '{alias_path}'"
            if icon_path:
                total_path = os.path.join(INSTALL.BASE_DIR, icon_path)
                command += f" -i '{total_path}'"

            os.system(command)

            print(f"Created shortcut for {source_loc} at {destination_loc} with name {name}")

        @staticmethod
        def daemon_startup(file_loc):
            if not INSTALL.new_install:
                return

            BASE_DIR = INSTALL.BASE_DIR
            new_str=str(file_loc).replace("/", "_")

            # Create the launchd plist content
            plist_content = f"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <plist version="1.0">
            <dict>
                <key>Label</key>
                <string>torrentlan.startup.{new_str}</string>
                <key>ProgramArguments</key>
                <array>
                    <string>{INSTALL.py}</string>
                    <string>{file_loc}</string>
                </array>
                <key>RunAtLoad</key>
                <true/>
                <key>WorkingDirectory</key>
                <string>{BASE_DIR}</string>
            </dict>
            </plist>
            """

            # Define the launchd plist path
            plist_file_path = os.path.expanduser(f"~/Library/LaunchAgents/torrentlan.startup.{new_str}.plist")

            # Write the launchd plist file
            with open(plist_file_path, "w") as plist_file:
                plist_file.write(plist_content)

            # Load the launchd plist file
            os.system(f"launchctl load {plist_file_path}")

            print(f"Created startup daemon for {file_loc}")

        @staticmethod
        def daemon_networkchange(file_loc):
            if not INSTALL.new_install:
                return

            BASE_DIR = INSTALL.BASE_DIR
            new_str=str(file_loc).replace("/", "_")

            # Create the launchd plist content
            plist_content = f"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <plist version="1.0">
            <dict>
                <key>Label</key>
                <string>torrentlan.networkchange.{new_str}</string>
                <key>ProgramArguments</key>
                <array>
                    <string>{INSTALL.py}</string>
                    <string>{file_loc}</string>
                </array>
                <key>WatchPaths</key>
                <array>
                    <string>/Library/Preferences/SystemConfiguration/NetworkInterfaces.plist</string>
                </array>
                <key>WorkingDirectory</key>
                <string>{BASE_DIR}</string>
            </dict>
            </plist>
            """

            # Define the launchd plist path
            plist_file_path = os.path.expanduser(f"~/Library/LaunchAgents/torrentlan.networkchange.{new_str}.plist")

            # Write the launchd plist file
            with open(plist_file_path, "w") as plist_file:
                plist_file.write(plist_content)

            # Load the launchd plist file
            os.system(f"launchctl load {plist_file_path}")

            print(f"Created network change daemon for {file_loc}")

        @staticmethod
        def daemon_time(file_loc,recur_time_min):
            if not INSTALL.new_install:
                return

            BASE_DIR = INSTALL.BASE_DIR
            new_str=str(file_loc).replace("/", "_")

            # Create the launchd plist content
            plist_content = f"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <plist version="1.0">
            <dict>
                <key>Label</key>
                <string>torrentlan.time.{new_str}</string>
                <key>ProgramArguments</key>
                <array>
                    <string>{INSTALL.py}</string>
                    <string>{file_loc}</string>
                </array>
                <key>StartCalendarInterval</key>
                <dict>
                    <key>Minute</key>
                    <integer>{recur_time_min}</integer>
                </dict>
                <key>WorkingDirectory</key>
                <string>{BASE_DIR}</string>
            </dict>
            </plist>
            """

            # Define the launchd plist path
            plist_file_path = os.path.expanduser(f"~/Library/LaunchAgents/torrentlan.time.{new_str}.plist")

            # Write the launchd plist file
            with open(plist_file_path, "w") as plist_file:
                plist_file.write(plist_content)

            # Load the launchd plist file
            os.system(f"launchctl load {plist_file_path}")

            print(f"Created time daemon for {file_loc} with recur time {recur_time_min} min")


    def main():
        
        if len(sys.argv) < 2:
            INSTALL.ALL_PLATFORMS.copy_to_program_files()        
            try:
                subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=INSTALL.BASE_DIR, check=True)
            except :
                print(f"Error installing requirements, please goto {INSTALL.BASE_DIR} and run 'pip install -r requirements.txt' and make sure it executes successfully")
                input("Press enter to exit")
                return


        if not INSTALL.new_install:
            print("TorrentLAN updated successfully")
            input("Press enter to exit")
            return
        

        ################ Below Codes is for first time installation only

        if platform.system() == "Windows":
            rc = 0
            if not INSTALL.WINDOWS.window_is_admin():
                # print ("Not admin.", os.getpid(), "params: ", sys.argv)
                path=INSTALL.WINDOWS.get_user_directory()
                arg1=base64.b64encode(path.encode('utf-8')).decode('utf-8')
                rc = INSTALL.WINDOWS.runAsAdmin_windows(arg1)
            else:
                # print("Admin!", os.getpid(), "params: ", sys.argv)
                try:
                    # if dev then use arg1=sys.argv[1] else arg1=sys.argv[2] during installation(due to pyinstaller)
                    if os.getcwd().endswith("TorrentLAN"):
                        arg1=sys.argv[1]
                    else:
                        arg1=sys.argv[2]
                    path=(base64.b64decode(arg1)).decode('utf-8')
                    INSTALL.ALL_PLATFORMS.run_once("utils/identity/main.py")
                    INSTALL.ALL_PLATFORMS.run_once("utils/tracker/client_ip_reg(c-s).py")
                    INSTALL.WINDOWS.create_shortcut(os.path.join(INSTALL.BASE_DIR, "data"), os.path.join(path,"Documents"), "TorrentLAN")
                    INSTALL.WINDOWS.create_shortcut(os.path.join(INSTALL.BASE_DIR, "data"), os.path.join(path,"Desktop"), "TorrentLAN")
                    INSTALL.WINDOWS.create_shortcut(os.path.join(INSTALL.BASE_DIR, "torrentlan_launcher","torrentlan_start.exe"), os.path.join(path,"Desktop"), "TorrentLAN.exe","./docs/Logo/Icon.ico")
                    INSTALL.WINDOWS.daemon_startup(os.path.join("utils", "file_transfer", "node.py"))
                    INSTALL.WINDOWS.daemon_time(os.path.join("utils", "file_transfer", "node.py"),5)
                    INSTALL.WINDOWS.daemon_startup(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"))
                    INSTALL.WINDOWS.daemon_time(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"),5)
                    INSTALL.WINDOWS.daemon_time(os.path.join("utils", "tracker", "client(c-s).py"),60*6)

                    print("Data of TorrentLAN is stored in the Documents folder, and TorrentLAN can be started from the desktop shortcut")
                    print("If prompt of a firewall appear then allow it(you can read about it in privacy & conncern of TorrentLAN in github)")
                    command=sys.executable + "utils/file_transfer/node.py"
                    subprocess.run(command, cwd=INSTALL.BASE_DIR, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    time.sleep(1)
                    print("Installation completed !!!!!!!!!")
                except Exception as e:
                    print(e)
                    print("Installation failed !!!!!!!!!")
                input("Press enter to exit")
                rc = 0
            return rc
                
        elif platform.system() == "Linux":
            INSTALL.ALL_PLATFORMS.run_once("utils/identity/main.py")
            INSTALL.ALL_PLATFORMS.run_once("utils/tracker/client_ip_reg(c-s).py")
            INSTALL.LINUX.create_shortcut(os.path.join(INSTALL.BASE_DIR, "data"), os.path.expanduser("~" + os.getlogin())+"/Documents", "TorrentLAN")
            INSTALL.LINUX.create_shortcut(os.path.join(INSTALL.BASE_DIR, "torrentlan_launcher","torrentlan_start"), os.path.expanduser("~/Desktop"), "TorrentLAN","./docs/Logo/Icon.ico")
            INSTALL.LINUX.daemon_startup(os.path.join("utils", "file_transfer", "node.py"))
            # INSTALL.LINUX.daemon_networkchange(os.path.join("utils", "file_transfer", "node.py"))
            INSTALL.LINUX.daemon_time(os.path.join("utils", "file_transfer", "node.py"),5)
            INSTALL.LINUX.daemon_startup(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"))
            # INSTALL.LINUX.daemon_networkchange(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"))
            INSTALL.LINUX.daemon_time(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"),5)
            INSTALL.LINUX.daemon_time(os.path.join("utils", "tracker", "client(c-s).py"),60*6)
        elif platform.system() == "Darwin":
            INSTALL.ALL_PLATFORMS.run_once("utils/identity/main.py")
            INSTALL.ALL_PLATFORMS.run_once("utils/tracker/client_ip_reg(c-s).py")
            INSTALL.MAC.create_shortcut(os.path.join(INSTALL.BASE_DIR, "data"), os.path.expanduser("~" + os.getlogin())+"/Documents", "TorrentLAN")
            INSTALL.MAC.create_shortcut(os.path.join(INSTALL.BASE_DIR, "torrentlan_launcher","torrentlan_start"), os.path.expanduser("~/Desktop"), "TorrentLAN","./docs/Logo/Icon.ico")
            INSTALL.MAC.daemon_startup(os.path.join("utils", "file_transfer", "node.py"))
            INSTALL.MAC.daemon_networkchange(os.path.join("utils", "file_transfer", "node.py"))
            INSTALL.MAC.daemon_startup(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"))
            INSTALL.MAC.daemon_networkchange(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"))
            INSTALL.MAC.daemon_time(os.path.join("utils", "tracker", "client(c-s).py"),60*6)
        else:
            print("Unsupported OS")
            input("Press enter to exit")
            return
            
        print("You can now close the window !!")
        print("Data of TorrentLAN is stored in the Documents folder, and TorrentLAN can be started from the desktop shortcut")
        print("If prompt of a firewall appear then allow it(you can read about it in privacy & conncern of TorrentLAN in github)")
        time.sleep(2)


        BASE_DIR=INSTALL.BASE_DIR
        command="python " + "utils/file_transfer/node.py"
        if platform.system=='Linux':
            subprocess.run("sudo -u "+INSTALL.user+" "+command, cwd=BASE_DIR, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
if __name__ == "__main__":
    # We use Runas in windows to increase privileges later
    if not INSTALL.WINDOWS.window_is_admin() and platform.system() != "Windows":
        print("Please run this script as an administrator/root !")
        input("Press enter to exit")
        sys.exit(1)


    INSTALL.main()
