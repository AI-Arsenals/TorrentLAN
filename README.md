# TorrentLAN

- A Torrent application to be used in Intranet
- Now you can download files with GBps speed, the only limitation is your computer's hardware

## Installation Guide

### Windows

- Goto [Windows_Installer](https://github.com/AI-Arsenals/TorrentLAN/releases/tag/Windows)
- Find the latest version (which is not beta) and inside '*assets*' click on `Windows_installer.exe` to download it
- From start menu, search cmd and open it as administrator
- Change to the directory where the .exe file is downloaded
- Run the downloaded .exe to install the software eg- `TorrentLAN-1.0.0.exe` then press enter
- You can see all your data in `Documents/TorrentLAN` folder
- Now you can use the TorrentLAN application from start menu and desktop shortcut

### Linux

- Goto [Linux_Installer](https://github.com/AI-Arsenals/TorrentLAN/releases/tag/Windows)
- Find the latest version (which is not beta) and inside '*assets*' click on `Linux_installer.bin` to download it
- Open terminal and change to the directory where the .bin file is downloaded
- Run the downloaded .bin with sudo eg- `sudo ./TorrentLAN-1.0.0.bin` then press enter
- You can see all your data in `Documents/TorrentLAN` folder
- Now you can use the TorrentLAN application from start menu and desktop shortcut

### Mac

- It will be available soon, but you can follow developer guide given below which will atleast allow you to download files using TorrentLAN

## Developer Guide

### Windows & Linux & Mac

- Clone the repository or download it in zip format and extract it
- Open terminal and change to the directory where the repository is cloned or extracted
- run `pip install -r requirements.txt` (people who understand `env` can also go that way otherwise it is not needed)
- run `python ./utils/identity/main.py`
change to `./TorrentLAN/my-app` directory
- run `npm install` (this will download about 500MB of data)
- change to `./TorrentLAN` directory
- run `python ./django_for_frontend`
open another terminal and change to `./TorrentLAN/my-app` directory
- run `npm start`
now a window will be opened(not a browser window) and you can use the TorrentLAN application
