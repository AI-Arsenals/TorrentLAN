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
        BASE_DIR = "/usr/bin/TorrentLAN"
    elif platform.system() == "Darwin":
        BASE_DIR = "/Applications/TorrentLAN"
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
            subprocess.Popen(command, cwd=INSTALL.BASE_DIR, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)

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
            batch_file_path = os.path.join(daemons_folder_path, "TorrentLAN - (Run on Startup) - " + str(file_loc).replace("\\", "_")+".bat")
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
        def daemon_networkchange(file_loc):
            if not INSTALL.new_install:
                return
            
            BASE_DIR = INSTALL.BASE_DIR

            daemons_folder_path = os.path.join(BASE_DIR,'daemons')
            # Create a batch file to change directory and run the daemon script
            batch_file_path = os.path.join(daemons_folder_path, "TorrentLAN - (Network Change Daemon) - " + str(file_loc).replace("\\", "_")+".bat")
            with open(batch_file_path, 'w') as f:
                f.write('@echo off\n')
                f.write(f'cd /d "{BASE_DIR}"\n')
                f.write(f'start /B /MIN"" "pythonw" "{file_loc}"')

            # Create a scheduled task to run the batch file every 5 minutes
            task_name = "TorrentLAN - (Network Change Daemon) - " + str(file_loc).replace("\\", "_")
            task_command = f'schtasks /create /tn "\\TorrentLAN\\{task_name}" /tr "cmd.exe /c \\"{batch_file_path}\\"" /sc minute /mo 10 /F'
            subprocess.run(task_command, shell=True)
            
            print(f"Created network change daemon for {file_loc}")

    class LINUX:
        @staticmethod
        def create_shortcut(source_loc, destination_loc,name):
            if not INSTALL.new_install:
                return

            # Create the shortcut file
            shortcut_path = os.path.join(destination_loc, name + ".desktop")

            if os.path.isfile(shortcut_path):
                Icon="file"
            else:
                Icon="folder"
            with open(shortcut_path, "w") as shortcut_file:
                shortcut_file.write(
                    f"[Desktop Entry]\nName={name}\nComment=TorrentLAN\nExec={source_loc}\nIcon={Icon}"
                )
            
            print(f"Created shortcut for {source_loc} at {shortcut_path} with name {name}")


        @staticmethod
        def daemon_startup(file_loc):
            if not INSTALL.new_install:
                return

            BASE_DIR = INSTALL.BASE_DIR

            # Service file content
            service_content = f"""\
            [Unit]
            Description=TorrentLAN - (Startup) - {str(file_loc)} 
            After=network.target

            [Service]
            ExecStart={INSTALL.py} {file_loc}
            WorkingDirectory={BASE_DIR}

            [Install]
            WantedBy=default.target
            """

            daemon_folder_path = os.path.join('/etc/systemd/system', 'torrentlan')
            os.makedirs(daemon_folder_path, exist_ok=True)
            
            service_file_path = os.path.join(daemon_folder_path, 'TorrentLAN - (Startup) - ' + str(file_loc) + '.service')
            with open(service_file_path, 'w') as service_file:
                service_file.write(service_content)

            os.system("systemctl daemon-reload")
            os.system(f'systemctl enable {service_file_path}')

            print(f"Created startup daemon for {file_loc}")

        @staticmethod
        def daemon_networkchange(file_loc):
            if not INSTALL.new_install:
                return

            BASE_DIR = INSTALL.BASE_DIR

            # Service file content
            service_content = f"""\
            [Unit]
            Description=TorrentLAN - (Network Change) - {str(file_loc)}

            [Service]
            Type=simple
            ExecStart={INSTALL.py} {file_loc}
            WorkingDirectory={BASE_DIR}

            [Install]
            WantedBy=network.target
            """

            daemon_folder_path = os.path.join('/etc/systemd/system', 'torrentlan')
            os.makedirs(daemon_folder_path, exist_ok=True)

            # Write the service file
            service_file_path = os.path.join(daemon_folder_path, 'TorrentLAN - (Network Change) - ' + str(file_loc) + '.service')
            with open(service_file_path, 'w') as service_file:
                service_file.write(service_content)

            os.system("systemctl daemon-reload")
            os.system(f"systemctl enable {service_file_path}")

            print(f"Created network change daemon for {file_loc}")

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

            # Create the launchd plist content
            plist_content = f"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <plist version="1.0">
            <dict>
                <key>Label</key>
                <string>torrentlan.startup.{str(file_loc)}</string>
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
            plist_file_path = os.path.expanduser(f"~/Library/LaunchAgents/torrentlan.startup.{str(file_loc)}.plist")

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

            # Create the launchd plist content
            plist_content = f"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <plist version="1.0">
            <dict>
                <key>Label</key>
                <string>torrentlan.networkchange.{str(file_loc)}</string>
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
            plist_file_path = os.path.expanduser(f"~/Library/LaunchAgents/torrentlan.networkchange.{str(file_loc)}.plist")

            # Write the launchd plist file
            with open(plist_file_path, "w") as plist_file:
                plist_file.write(plist_content)

            # Load the launchd plist file
            os.system(f"launchctl load {plist_file_path}")

            print(f"Created network change daemon for {file_loc}")


    def main():
        INSTALL.ALL_PLATFORMS.copy_to_program_files()
        INSTALL.ALL_PLATFORMS.run_once("utils/identity/main.py")
        INSTALL.ALL_PLATFORMS.run_once("utils/tracker/client_ip_reg(c-s).py")
        INSTALL.ALL_PLATFORMS.run_once("utils/file_transfer/node.py")

        if platform.system() == "Windows":
            INSTALL.WINDOWS.create_shortcut(os.path.join(INSTALL.BASE_DIR, "data"), os.path.expanduser("~/Documents"), "TorrentLAN")
            INSTALL.WINDOWS.daemon_startup(os.path.join("utils", "file_transfer", "node.py"))
            INSTALL.WINDOWS.daemon_networkchange(os.path.join("utils", "file_transfer", "node.py"))
            INSTALL.WINDOWS.daemon_startup(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"))
            INSTALL.WINDOWS.daemon_networkchange(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"))
        elif platform.system() == "Linux":
            INSTALL.LINUX.create_shortcut(os.path.join(INSTALL.BASE_DIR, "data"), os.path.expanduser("~/Documents"), "TorrentLAN")
            INSTALL.LINUX.daemon_startup(os.path.join("utils", "file_transfer", "node.py"))
            INSTALL.LINUX.daemon_networkchange(os.path.join("utils", "file_transfer", "node.py"))
            INSTALL.LINUX.daemon_startup(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"))
            INSTALL.LINUX.daemon_networkchange(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"))
        elif platform.system() == "Darwin":
            INSTALL.MAC.create_shortcut(os.path.join(INSTALL.BASE_DIR, "data"), os.path.expanduser("~/Documents"), "TorrentLAN")
            INSTALL.MAC.daemon_startup(os.path.join("utils", "file_transfer", "node.py"))
            INSTALL.MAC.daemon_networkchange(os.path.join("utils", "file_transfer", "node.py"))
            INSTALL.MAC.daemon_startup(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"))
            INSTALL.MAC.daemon_networkchange(os.path.join("utils", "tracker", "client_ip_reg(c-s).py"))
        
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
    if not check_admin():
        print("Please run this script as an administrator/root !")
        exit()
    INSTALL.main()
