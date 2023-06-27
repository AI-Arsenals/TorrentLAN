from utils.identity.main import set_user_name
from utils.file_transfer.main import *
from utils.db_manage.db_create import main as db_create_main

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
    """

    files = []
    folders = []
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

    value = create_link
    db_create_main(FORCE_UPDATE=True)
    update_server_with_db()
    update_server_with_ip()

    return value


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
