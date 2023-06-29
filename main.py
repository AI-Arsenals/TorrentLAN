from utils.identity.main import set_user_name
from utils.file_transfer.main import *
from utils.db_manage.db_create import main as db_create_main
from utils.db_manage.symlink_maker import create_symlink

module_path = "utils/tracker/client(c-s).py"
spec = import_util.spec_from_file_location(None, module_path)
module = import_util.module_from_spec(spec)
spec.loader.exec_module(module)
update_server_with_db = getattr(module, "check_updation")

module_path = "utils/tracker/client_ip_reg(c-s).py"
spec = import_util.spec_from_file_location(None, module_path)
module = import_util.module_from_spec(spec)
spec.loader.exec_module(module)
update_server_with_ip = getattr(module, "update")

module_path = "utils/tracker/shared_util/fetch_childs(c-s).py"
spec = import_util.spec_from_file_location(None, module_path)
module = import_util.module_from_spec(spec)
spec.loader.exec_module(module)
fetch_childs = getattr(module, "fetch_childs")

module_path = "utils/tracker/shared_util/fetch_rows_at_depth(c-s).py"
spec = import_util.spec_from_file_location(None, module_path)
module = import_util.module_from_spec(spec)
spec.loader.exec_module(module)
fetch_rows_at_depth = getattr(module, "fetch_rows_at_depth")

module_path = "utils/extra tools/web_downloader/main.py"
spec = import_util.spec_from_file_location(None, module_path)
module = import_util.module_from_spec(spec)
spec.loader.exec_module(module)
web_download = getattr(module, "main")

def set_username(user_name: str) -> bool:
    """
    --identity setup
    -run at first time when frontend is started
    -can change later using the settings in frontend

    Arguments:
        user_name (str): User Name to set

    Returns:
        bool: True if success else False
    """

    value = set_user_name(user_name)
    return value


def download(unique_id: str, lazy_file_hash: str, table_name: str = "Normal_Content_Main_Folder") -> bool:
    """
    --file transfer download
    -setup db and ips
    -download file from nodes

    Arguments:
        unique_id (str): Unique ID of file
        lazy_file_hash (str): Lazy File Hash of file
        table_name (str): Table Name of file (Currently let it be "Normal_Content_Main_Folder")

    Returns:
        bool: True if success else False if partial or full download failure
    """

    """Frontend api where i will send 
    api_func(tuple(unique_id(str), lazy_file_hash(str), table_name(str),download_percentage(float)))
    """

    value = DOWNLOAD_FILE_CLASS.main(
        unique_id, lazy_file_hash, table_name, api_func)
    return value


def uniqueid_is_up(unique_id: str) -> tuple(bool, float):
    """
    --check if a unique id is up

    Arguments:
        unique_id (str): Unique ID of file

    Returns:
        bool: True if up else False
        float: speed in bytes per second if True else 0
    """

    val1, val2 = DOWNLOAD_FILE_CLASS.uniqueid_is_up(unique_id)
    return val1, val2


def childs(unique_id: str, lazy_file_hash: str) -> tuple(list, list):
    """
    --get childs of a unique id

    Arguments:
        unique_id (str): Unique ID of file
        lazy_file_hash (str): Lazy File Hash of file

    Returns:
        list: list of childs which are files
        list: list of childs which are folders

        If some error occured during transmission or (lazy_file_hash and unique_id) cannot be found then it returns False, False
    """

    files, folders = fetch_childs(unique_id, lazy_file_hash)
    return files, folders


def upload_file(path: str) -> bool:
    """
    --file upload for seeding
    -update db
    -upload server with new db
    -do ip registration

    Arguments:
        path (str): Path of file to upload

    Returns:
        bool: True if success else False
    """

    # value = create_link
    db_create_main(FORCE_UPDATE=True)
    update_server_with_db()
    update_server_with_ip()

    # return value


def db_update() -> bool:
    """
    --update db
    -update server with new db
    -do ip registration

    Returns:
        bool: True if success else False
    """

    db_create_main(FORCE_UPDATE=True)
    update_server_with_db()
    update_server_with_ip()

    return True

def rows_at_depth(depth : int, folder_name = None) -> tuple(list,list):
    """
    --Finds rows at particular depth
    - if 'depth'=0 or 'depth'=1 then no need to provide 'folder_name'
    - depth 0 means it returns table names in dbs, eg-Normal_Content_Folder
    - depth 1 means Movies,Music,Games
    - depth > 1 , u need to specify depth accordingly and 'folder_name' show be equal to name of parent of the rows at the depth u want

    Arguments:
        depth (int) : depth at while the files u want to see
    
    Returns :
        files (list) : list of tuples and each tuple is same as a row in db, the tuples are of only file
        folders (list) : list of tuples and each tuple is same as a row in db, the tuples are of only folder
    """

    files,folders=fetch_rows_at_depth(depth,folder_name)
    return files,folders

def web_downloader(url : str, output_filename=None,output_dir=None):
    """
    -- downloads files from web using multiple fragments download, it is useful when server hosting the file limits a single download speed
    
    Arguments:
        url (str) : url of the file to download
        output_filename (str) : if u want to yourself specify the filename (Default is os.path.basename(url))
        output_dir(str) : if u want to specify download location (Default is data/Web_downloader)
    """

    web_download(url,output_filename,output_dir)

def upload(source_path : str, dest_dir : str):
    """
    --create a symlink
    - frontend should ask user source_path and then some inapp ui based to make them select the path
    - the symlink is created with same name as of the file/folder name of source_path
    - if the user OS is windows then frontend should notify before hand that he need to click yes in popup to upload file, if the user doesn't want to do that, then open the folder of ./data and tell the user to put the data accordingly (eg - inside ./data/Normal/Games)

    Arguments:
        source_path (str) : path of a file or folder that is to be uploaded
        dest_path (str) :  path where the pointer(symlink) [eg- ./data/Normal/Games if we suppose source_path is a game] 
    """

    create_symlink(source_path,dest_dir)
    db_update()
