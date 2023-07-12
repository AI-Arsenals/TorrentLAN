import os
import platform
import sys

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..')))
from utils.log.main import log

def create_symlink(source_path,dest_dir):
    source_path=os.path.realpath(source_path)
    source_name=os.path.split(source_path)[-1]
    dest_path = os.path.realpath(dest_dir + os.sep + source_name)
    source_path=os.path.realpath(source_path)
    dest_path=os.path.realpath(dest_path)
    # print(dest_path)
    try:
        if platform.system()=="Windows":
            import ctypes
            def window_is_admin():
                try:
                    return ctypes.windll.shell32.IsUserAnAdmin()
                except:
                    return False
            if not window_is_admin():
                # Re-launch the script with administrative privileges
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
                return
        
        os.symlink(source_path,dest_path)
        log(f"Symlink created successfully from {source_path} to {dest_path}")
    except OSError as e:
        log(f"Failed to create symbolic link: {e}",2)

if __name__=="__main__":
    create_symlink("./",r"C:\Users\prakh\Desktop\Home")