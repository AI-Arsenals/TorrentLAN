import subprocess
import tempfile
import os
import sys
import shutil
import platform


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
            command=INSTALL.py + " " + file_loc
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
            print(f"Copying complete")

    class WINDOWS:
        @staticmethod
        def create_shortcut(source_loc, destination_loc,name):
            if not INSTALL.new_install:
                return
            import win32com.client
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(os.path.join(destination_loc, name + ".lnk"))
            shortcut.Targetpath = source_loc
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

            # Create a batch file to change directory and run the daemon script
            batch_file_path = os.path.join(daemons_folder_path, "TorrentLAN - (Run on Startup) - " + str(file_loc).replace("\\", "_").replace("\\", "_")+".bat")
            with open(batch_file_path, 'w') as f:
                f.write('@echo off\n')
                f.write(f'cd /d "{BASE_DIR}"\n')
                f.write(f'start /B /MIN"" "pythonw" "{file_loc}"')

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

            # Run the batch file
            action_startup = task_startup.Actions.Create(0)  # 0 represents "Execute" action
            action_startup.Path = "cmd.exe"
            action_startup.Arguments = f'/c "{batch_file_path}"'

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
            # Create a batch file to change directory and run the daemon script
            batch_file_path = os.path.join(daemons_folder_path, "TorrentLAN - (Network Change Daemon) - " + str(file_loc).replace("\\", "_")+".bat")
            with open(batch_file_path, 'w') as f:
                f.write('@echo off\n')
                f.write(f'cd /d "{BASE_DIR}"\n')
                f.write(f'start /B /MIN"" "pythonw" "{file_loc}"')

            # Create a scheduled task to run the batch file every 5 minutes
            task_name = "TorrentLAN - (Network Change Daemon) - " + str(file_loc).replace("\\",  "_")
            task_command = f'schtasks /create /tn "\\TorrentLAN\\{task_name}" /tr "cmd.exe /c \\"{batch_file_path}\\"" /sc minute /mo {recur_time_min} /F'
            subprocess.run(task_command, shell=True)
            
            print(f"Created network change daemon for {file_loc}")

    class LINUX:
        @staticmethod
        def create_shortcut(source_loc, destination_loc, name):
            if not INSTALL.new_install:
                return
            shortcut_path = os.path.join(destination_loc, name)

            if os.path.exists(shortcut_path):
                print(f"Shortcut already exists at {shortcut_path}")
            else:
                subprocess.run(["ln", "-s", source_loc, shortcut_path])
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
        def create_shortcut(source_loc, destination_loc, name):
            if not INSTALL.new_install:
                return

            # Create the alias (shortcut)
            alias_path = os.path.join(destination_loc, name + ".alias")

            # Create the alias using the 'os' module
            os.system(f"ln -s '{source_loc}' '{alias_path}'")

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
        INSTALL.ALL_PLATFORMS.copy_to_program_files()
        INSTALL.ALL_PLATFORMS.run_once("utils/identity/main.py")
        INSTALL.ALL_PLATFORMS.run_once("utils/tracker/client_ip_reg(c-s).py")

        if platform.system() == "Windows":
            INSTALL.WINDOWS.create_shortcut(os.path.join(INSTALL.BASE_DIR, "data"), os.path.expanduser("~/Documents"), "TorrentLAN")
            INSTALL.WINDOWS.daemon_startup(os.path.join("utils", "file_transfer", "node.py"))
            INSTALL.WINDOWS.daemon_time(os.path.join("utils", "file_transfer", "node.py"),5)
            INSTALL.WINDOWS.daemon_startup(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"))
            INSTALL.WINDOWS.daemon_time(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"),5)
            INSTALL.WINDOWS.daemon_time(os.path.join("utils", "tracker", "client(c-s).py"),60*6)
        elif platform.system() == "Linux":
            INSTALL.LINUX.create_shortcut(os.path.join(INSTALL.BASE_DIR, "data"), os.path.expanduser("~" + os.getlogin())+"/Documents", "TorrentLAN")
            INSTALL.LINUX.daemon_startup(os.path.join("utils", "file_transfer", "node.py"))
            # INSTALL.LINUX.daemon_networkchange(os.path.join("utils", "file_transfer", "node.py"))
            INSTALL.LINUX.daemon_time(os.path.join("utils", "file_transfer", "node.py"),5)
            INSTALL.LINUX.daemon_startup(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"))
            # INSTALL.LINUX.daemon_networkchange(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"))
            INSTALL.LINUX.daemon_time(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"),5)
            INSTALL.LINUX.daemon_time(os.path.join("utils", "tracker", "client(c-s).py"),60*6)
        elif platform.system() == "Darwin":
            INSTALL.MAC.create_shortcut(os.path.join(INSTALL.BASE_DIR, "data"), os.path.expanduser("~" + os.getlogin())+"/Documents", "TorrentLAN")
            INSTALL.MAC.daemon_startup(os.path.join("utils", "file_transfer", "node.py"))
            INSTALL.MAC.daemon_networkchange(os.path.join("utils", "file_transfer", "node.py"))
            INSTALL.MAC.daemon_startup(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"))
            INSTALL.MAC.daemon_networkchange(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"))
            INSTALL.MAC.daemon_time(os.path.join("utils", "tracker", "client(c-s).py"),60*6)
        
        if INSTALL.new_install:
            print("Installation complete !!!!!!!!!")
        else:
            print("Updation complete !!!!!!!!!")
        print("You can now close the window !!")

# Check privileges
def check_admin():
    if platform.system() == "Windows":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        return os.geteuid() == 0
    else:
        return False
    
if __name__ == "__main__":
    # check privileges
    # if not check_admin():
    #     print("Please run this script as an administrator/root !")
    #     sys.exit(1)
    INSTALL.main()
