# TorrentLAN

- A Torrent application to be used in Intranet
- Now you can download files with GBps speed, the only limitation is your computer's hardware

---
## Privacy & Concern

- We don't ask any of your personal information
- If you think our program can be malicious so you can yourself scan with a antivirus
- We have also uploaded the results of our scan from multiple antivirus, It is present at the place where you download the installer, below are the scan results of the latest version of our Executables
![Windows_executable_scan](./docs/README/antivirus_scan_windows.png)
![Linux_executable_scan](./docs/README/antivirus_scan_linux.png)
- The sudo/root permission we are asking is just to add python script in (cron jobs/task sheduler) and (create shorcut if OS==windows), you can confirm the same in [intall.py](./install.py) file, if you are still not convinced then you can see that in [intall.py](./install.py) from line around "529" to "551" you can see that there are some functions named with daemons, these are the functions requiring privilege, so you can manually create cronjobs for these functions , after that remove the privilage restriction inside `__name__=='__main__` and then run the script. Additionally if you are an windows user then you must also make sure that every fxn calling `INSTALL.WINDOWS.create_shortcut` which creates shortcut you should make that shortcut manually
- You might encounter a firewall permission something like below **(you have to select both private and public as shown in image)** *{For those who want to know what this permission means-: When you connect to Wifi you might know that the connection is defined as private or public, so if the network on which server is connected is set as public in your pc, then only allowing permission on private network won't make TorrentLAN work properly}*
![Firewall_permission](./docs/README/firewall_permission.png)

---


## Installation Guide

### Windows

- Goto [Windows_Installer](https://github.com/AI-Arsenals/TorrentLAN/releases/tag/Windows)
- Find the latest version (which is not beta) and inside '*assets*' click on `Windows_installer.exe` to download it
- If firewall permission is asked in later process, then check the last point in [Privacy & Concern](#privacy--concern)
- From start menu, search cmd and open it as administrator
- Change to the directory where the .exe file is downloaded
- Run the downloaded .exe to install the software eg- `TorrentLAN-1.0.0.exe` then press enter
- You can see all your data in `Documents/TorrentLAN` folder
- Now you can use the TorrentLAN application from start menu and desktop shortcut

### Linux

- Goto [Linux_Installer](https://github.com/AI-Arsenals/TorrentLAN/releases/tag/Windows)
- Find the latest version (which is not beta) and inside '*assets*' click on `Linux_installer.bin` to download it
- If firewall permission is asked in later process, then check the last point in [Privacy & Concern](#privacy--concern)
- Open terminal and change to the directory where the .bin file is downloaded
- Run the downloaded .bin with sudo eg- `sudo ./TorrentLAN-1.0.0.bin` then press enter
- You can see all your data in `Documents/TorrentLAN` folder
- Now you can use the TorrentLAN application from start menu and desktop shortcut

### Mac

- A installation executable is not yet available for Mac yet but u can still use in mac by following below procedute
- You must have python and nodejs installed on your computer
- Clone the repository or download it in zip format and extract it
- If firewall permission is asked in later process, then check the last point in [Privacy & Concern](#privacy--concern)
- Change directory to the folder TorrentLAN
- run `pip install -r requirements.txt` (people who understand `env` can also go that way otherwise it is not needed)
- run `python ./utils/identity/main.py`
- change to `./my-app` directory
- run `npm install` (this will download about 500MB of data) 
- Change directory to the folder TorrentLAN(i.e. base directory where you have downloaded TorrentLAN)
- run `python ./no_install_launch.py`

---
## Developer Guide

### Windows & Linux & Mac

- Clone the repository
- You must have python and nodejs installed on your computer
- Open terminal and change to the directory where the repository is cloned or extracted
- run `pip install -r requirements.txt` (people who understand `env` can also go that way otherwise it is not needed)
- run `python ./utils/identity/main.py`
- change to `./my-app` directory
- run `npm install` (this will download about 500MB of data)
- Change directory to the folder TorrentLAN(i.e. base directory where you have downloaded TorrentLAN)
- After the above setup any command you run should be from TorrentLAN base directory otherwise it will not work
- All the fxns of backend are available with details in `main.py`
- For People who are outside of (IITJ college) should follow [Outside IITJ College Guide](#outside-iitj-college-guide)

---
## Outside IITJ College Guide

- This guide is for people who are outside (IITJ college)
- TorrentLAN uses server-client tracker model, So u must setup a computer which will act as a tracker server
- In the server you should run `./utils/tracker/server(c-s).py`
- For the clients, change the 'server_addr' to your server address inside `./configs/server.json`
