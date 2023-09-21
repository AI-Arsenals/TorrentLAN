import os
import importlib.util as import_util
from utils.identity.main import set_user_name,show_user_name
from utils.file_transfer.main import DOWNLOAD_FILE_CLASS
from utils.db_manage.db_create import main as db_create_main
from utils.db_manage.symlink_maker import create_symlink
from utils.log.main import log
from utils.dashboard_db.main import fetch_all_entries,update_dashboard_db,delete_row_dashboard_db,search_dashboard_db
# from utils.django_utils.dashboard_cache import cache_fetch,cache_update
from utils.remover.log import fetch_logs_size,delete_logs
from utils.remover.tmp_downloads import fetch_tmp_size,delete_tmp
from utils.django_utils.send_base_dir import get_base_dir


module_path = "utils/tracker/client(c-s).py"
spec = import_util.spec_from_file_location("", module_path)
module = import_util.module_from_spec(spec)
spec.loader.exec_module(module)
update_server_with_db = getattr(module, "check_updation")

module_path = "utils/tracker/client_ip_reg(c-s).py"
spec = import_util.spec_from_file_location("", module_path)
module = import_util.module_from_spec(spec)
spec.loader.exec_module(module)
update_server_with_ip = getattr(module, "update")

module_path = "utils/tracker/shared_util/fetch_childs(c-s).py"
spec = import_util.spec_from_file_location("", module_path)
module = import_util.module_from_spec(spec)
spec.loader.exec_module(module)
fetch_childs = getattr(module, "fetch_childs")

module_path = "utils/tracker/shared_util/fetch_rows_at_depth(c-s).py"
spec = import_util.spec_from_file_location("", module_path)
module = import_util.module_from_spec(spec)
spec.loader.exec_module(module)
fetch_rows_at_depth = getattr(module, "fetch_rows_at_depth")

module_path = "utils/tracker/shared_util/search_db(c-s).py"
spec = import_util.spec_from_file_location("", module_path)
module = import_util.module_from_spec(spec)
spec.loader.exec_module(module)
search_db = getattr(module, "search_db")

module_path = "utils/extra tools/web_downloader/main.py"
spec = import_util.spec_from_file_location("", module_path)
module = import_util.module_from_spec(spec)
spec.loader.exec_module(module)
web_download = getattr(module, "main")

class INIT():
    def __init__(self):
        db_create_main()
        update_server_with_db()
        update_server_with_ip()
        log("INIT done", 0)

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

def show_username() -> str:
    """
    --show username
    -show username of the user

    Returns:
        str: username
    """

    val=show_user_name()
    return val


def download(unique_id: str, lazy_file_hash: str, table_name: str,name__api:str,file_loc__api:str,api_loc=None) -> tuple[str,bool]:
    """
    --file transfer download
    -setup db and ips
    -download file from nodes

    Arguments:
        unique_id (str): Unique ID of file
        lazy_file_hash (str): Lazy File Hash of file
        table_name (str): Table Name of file (Currently let it be "Normal_Content_Main_Folder")
        name__api (str): Name of the file (same as the name column in db)    
        file_loc__api (str): Location of the file (same as the file_loc in metadata column in db)
        api_loc (str): Url of the api where backend will do a GET request to update download progress (the data will be sent like - Eg-"http://localhost:8000/recv_download?afeaf3fwaf=50" where api_loc="http://localhost:8000/recv_download")
        -- when percentage is sent at api_loc please do max(current_percentage,percentage_received) also do min(recieved_percentage,100)
        
    Returns:
        bool: True if success else False if partial or full download failure
        lazy_file_hash: return lazy_file_hash provided as arguments in function
    """

    """Frontend api where i will send 
    api_func(tuple(unique_id(str), lazy_file_hash(str), table_name(str),download_percentage(float)))
    """

    value = DOWNLOAD_FILE_CLASS.main(
        unique_id, lazy_file_hash, table_name,name__api,file_loc__api,api_loc)
    return value,lazy_file_hash


def uniqueid_is_up(unique_id: str) -> tuple[bool, float]:
    """
    --check if a unique id is up

    Arguments:
        unique_id (str): Unique ID of file

    Returns:
        bool: True if up else False
        float: speed in bytes per second if bool==true else 0
    """

    try:
        val1, val2 = DOWNLOAD_FILE_CLASS.up_check(unique_id)
        return val1, val2
    except Exception as e:
        log(f"Error in uniqueid_is_up : {e}")
        return False, 0


def childs(unique_id: str, lazy_file_hash: str) -> tuple[list, list]:
    """
    --get childs of a unique id

    Arguments:
        unique_id (str): Unique ID of file
        lazy_file_hash (str): Lazy File Hash of file

    Returns:
        list: list of childs which are files
        list: list of childs which are folders

        return False,False if some error occured during transmission or (lazy_file_hash and unique_id) cannot be found
    """

    files, folders = fetch_childs(unique_id, lazy_file_hash)
    return files, folders


def db_update() -> bool:
    """
    --update db
    -update server with new db
    -do ip registration
    - no need to handle case of return False as it is not necessary that we must update the server

    Returns:
        bool: True if success else False
    """

    db_create_main(FORCE_UPDATE=True)
    update_server_with_db()
    update_server_with_ip()

    return True


def rows_at_depth(depth: int, folder_name=None):
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

        return False,False if any error occured during transmission or other fault
    """

    files, folders = fetch_rows_at_depth(depth, folder_name)
    return files, folders


def web_downloader(url: str, output_filename=None, output_dir=None,api_loc=None)->tuple[bool,str]:
    """
    -- downloads files from web using multiple fragments download, it is useful when server hosting the file limits a single download speed

    Arguments:
        url (str) : url of the file to download
        output_filename (str) : if u want to yourself specify the filename (Default is os.path.basename(url))
        output_dir(str) : if u want to specify download location (Default is data/Web_downloader)
        api_loc (str): Url of the api where backend will do a GET request to update download progress (the data will be sent like - Eg-"http://localhost:8000/recv_download?afeaf3fwaf=50" where api_loc="http://localhost:8000/recv_download")
        -- when percentage is sent at api_loc please do max(current_percentage,percentage_received) also do min(recieved_percentage,100)
    Returns :
        bool : True if success else False
        url (str): return url as same as provided in arguments
    """

    res=web_download(url, output_filename, output_dir,api_loc)
    return res,url


def upload(source_paths: list, dest_dir: str) -> tuple[bool,list]:
    """
    --create a symlink
    - frontend should ask user source_path and then some inapp ui based to make them select the dest_dir
    - the symlink is created with same name as of the file/folder name of source_path
    - if the user OS is windows then frontend should notify before hand that he need to click yes in popup to upload file, if the user doesn't want to do that, then open the folder of ./data and tell the user to put the data accordingly (eg - inside ./data/Normal/Games)

    Arguments:
        source_paths (str) : paths of files and folders that is to be uploaded
        dest_path (str) :  path where the pointer(symlink) [eg- ./data/Normal/Games if we suppose source_path is a game] 

    Returns:
        bool: True if all symlinks are created else False
        list: bool(or 0,1) array representing which symlink is created and which is not corresponding to index of source_paths 
    """
    if len(source_paths) == 0 or dest_dir == "":
        log("source_path or dest_dir is empty", 2)
        return False
    res,arr=create_symlink(source_paths, dest_dir)
    if(res==False):
        return False,arr
    db_update()
    return True,arr


def db_search(search_bys: list, searchs: list):
    """
    --Searches with AND filter in db
    - search_bys is list of columns to search in
    - searchs is list of values to search for
    - the value in searchs are the mapping to the columns in search_bys
    - current columns that can be searched=[id,name,is_file,parent_id,child_id,metadata,lazy_file_check_hash,unique_id,hash]
    - eg = db_search(["name","unique_id"],["main","041279ea-3370-40a8-a094-e9cbb5a389f2"])
    

    Arguments:
        search_bys (list) : list of columns to search in
        searchs (list) : list of values to search for

    Returns :
        list : list of tuples and each tuple is same as a row in db [return False if any error occured during transmission]

        return False if any error occured during transmission or other fault
    """

    results = search_db(search_bys, searchs)
    return results

def fetch_base_dir()->str:
    """
    - returns the base dir
    """
    return get_base_dir()

def file_location_opener(file_location:str)->bool:
    """
    - opens the file location in the file explorer
    - returns True if success else False
    """
    BASE_DIR=get_base_dir()
    try:
        # check if BASE_DIR is in file_location
        if not (BASE_DIR in file_location):
            file_location=os.path.join(BASE_DIR,file_location)
        file_location=os.path.realpath(file_location)

        # check if BASE_DIR is in file_location
        if not (BASE_DIR in file_location):
            log("file_location_opener : file_location is not in BASE_DIR",2)
            # report suspicious activity
            return False
        # if(os.path.isfile(file_location)):
            # os.startfile(file_location)
        # else:
            # one_dir_back=os.path.dirname(file_location)
            # # highlight file in explorer
            # os.startfile(one_dir_back)
        os.startfile(file_location)
        return True
    except Exception as e:
        log(f"Error in file_location_opener : {e}")
        return False
    
class dashboard_fxns():
    # def cache_fetcher(only_fetch=False):
    #     """
    #     --fetches cache data
    #     - returns the cache data
    #     - return False if cache is not initialized yet

    #     ----- Please note that if you do cache_fetcher without setting only_fetch=True, then you won't be able to do cache_fetcher from another process until that same process do cache_updater
    #     """
    #     return cache_fetch(only_fetch)
    
    # def cache_updater(cache_data):
    #     """
    #     --updates cache data

    #     """
    #     return cache_update(cache_data)
    
    def fetch_dashboard_db():
        """
        --fetches dashboard db
        - returns the dashboard db
        - the format of dashboard db can be checked at utils.dashboard_db.main
        - for download the format eg- {update_dashboard_db('Download',name__api,unique_id__api,lazy_file_hash__api,table_name,0,TOTAL_SIZE,file_loc__api)}
        - for url download the format eg- {update_dashboard_db('Download',output_filename,'Web',lazy_file_hash.hexdigest(),'Web',0,file_size,str(os.path.realpath(output_filedir)))}

        """
        return fetch_all_entries()
    
    def updater_dashboard_db(download_or_upload:str, name:str, unique_id:str, lazy_file_hash:str, table_name:str, percentage:str, Size:str, file_location:str):
        """
        --updates dashboard db
        - updates dashboard db with the given data
        - the format of dashboard db can be checked at utils.dashboard_db.main     
        -- [need to shift to an inmemory db updation in later versions]

        Arguments:
            download_or_upload (str) : "Download" or "Upload"
            name (str) : name of the file
            unique_id (str) : unique_id of the file
            lazy_file_hash (str) : lazy_file_hash of the file
            table_name (str) : table_name of the file
            percentage (int) : percentage of the file
            Size (int) : Size of the file
            file_location (str) : file_location of the file

        """
        update_dashboard_db(download_or_upload, name, unique_id, lazy_file_hash, table_name, percentage, Size, file_location)

    def delete_row_in_dashboard_db(download_or_upload:str, lazy_file_hash:str):
        """
        -- delete a row in dashboard db

        Arguments:
            download_or_upload (str) : "Download" or "Upload"
            lazy_file_hash (str) : lazy_file_hash of the file
        """
        delete_row_dashboard_db(download_or_upload, lazy_file_hash)

    def search_in_dashboard_db(search_bys:list, searchs:list):
        """
        --Searches with AND filter in dashboard db
        - search_bys is list of columns to search in
        - searchs is list of values to search for
        - the value in searchs are the mapping to the columns in search_bys
        
        download_or_upload (str) : "Download" or "Upload"
        name (str) : name of the file
        unique_id (str) : unique_id of the file
        lazy_file_hash (str) : lazy_file_hash of the file
        table_name (str) : table_name of the file
        percentage (int) : percentage of the file
        Size (int) : Size of the file
        file_location (str) : file_location of the file
        

        Arguments:
            search_bys (list) : list of columns to search in
            searchs (list) : list of values to search for

        Returns :
            list : list of dictionary with keys as the columns and values as the values in the row
        """
        search_dashboard_db(search_bys, searchs)


class remover():
    def log_size_fetcher()->int:
        """
        --fetches logs size

        Returns:
            bool : the logs size in bytes
        """
        return fetch_logs_size()
    
    def log_remover():
        """
        --removes logs
        """
        return delete_logs()
    
    def tmp_folder_size_fetcher()->int:
        """
        --fetches tmp size

        Returns:
            bool : the tmp size in bytes
        """
        return fetch_tmp_size()
    
    def tmp_folder_remover():
        """
        --removes tmp
        - please make a note for user that deleting tmp may cause problems with the incomplete downloads

        """
        return delete_tmp()

if __name__=='__main__':
    download("b43b6944-f193-4f19-8010-6c22dacbf4c9","1a7131b3f5968315254372c86dc30317",table_name="Normal_Content_Main_Folder",name__api="test_name",file_loc__api="data/Normal/Games",api_loc="http://127.0.0.1:8000/api/progress")