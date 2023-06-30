import sys
import os
import json
import sqlite3
import threading
import heapq
import time
import base64
import queue
from termcolor import colored
import importlib.util as import_util

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from utils.log.main import log
from utils.file_transfer.live_ip_check import live_ip_checker
from utils.file_transfer.file_downloader import file_download

module_path = "utils/tracker/shared_util/client_uniqueid_to_ip_fetch(c-s).py"
spec =import_util.spec_from_file_location("", module_path)
module =import_util.module_from_spec(spec)
spec.loader.exec_module(module)
get_ips_and_netmasks = getattr(module, "get_ips_and_netmasks")

module_path = "utils/tracker/client_ip_reg(c-s).py"
spec =import_util.spec_from_file_location("", module_path)
module =import_util.module_from_spec(spec)
spec.loader.exec_module(module)
get_my_connect_ip=getattr(module, "get_my_connect_ip")
get_netmask=getattr(module, "get_netmask")
get_ip_address=getattr(module, "get_ip_address")

module_path = "utils/file_transfer/fetch_unique_id_from_hashes(c-s).py"
spec =import_util.spec_from_file_location("", module_path)
module =import_util.module_from_spec(spec)
spec.loader.exec_module(module)
fetch_unique_id_from_hashes=getattr(module, "fetch_unique_id_from_hashes")

module_path = "utils/file_transfer/sub_db_downloader(c-s).py"
spec =import_util.spec_from_file_location("", module_path)
module =import_util.module_from_spec(spec)
spec.loader.exec_module(module)
subdb_downloader=getattr(module, "subdb_downloader")

NODE_PORT=8890

C_S_model_SERVER_CONFIG="configs/server.json"
C_S_model_SERVER_ADDR=json.load(open(C_S_model_SERVER_CONFIG))["server_addr"]
CONFIG_FOLDER_LOCATION = "configs/folder_locations.json"
SUB_DB_PATH = "data/.db/sub_db_downloaded"
LIVE_IP_CHECK_CONFIG= "configs/live_ip_check_config.json"
SPEED_TEST_DATA_SIZE = json.load(open(LIVE_IP_CHECK_CONFIG))["speed_test_data_size"]
FILE_TRANSFER_MAIN_CONFIG = "configs/file_transfer_main_config.json"
json_data_file_transfer_main_config = json.load(open(FILE_TRANSFER_MAIN_CONFIG))
MAX_CONCURRENT_DOWNLOAD_TO_SINGLE_IP=json_data_file_transfer_main_config["max_concurrent_download_to_single_ip"]
BREAK_DOWNLOAD_WHEN_SIZE_EXCEED=json_data_file_transfer_main_config["break_download_when_size_exceed"]
IP_LOCK_TAKEN_BY_BIG_FILE_DOWNLOAD=json_data_file_transfer_main_config["ip_lock_taken_by_big_file_download"]
TMP_DOWNLOAD_DIR=json_data_file_transfer_main_config["tmp_download_dir"]
SIZE_AFTER_WHICH_FILE_IS_CONSIDERED_BIG=json_data_file_transfer_main_config["size_after_which_file_is_considered_big"]
HIGH_SPEED_THRESHOLD=json_data_file_transfer_main_config["high_speed_threshold"]
MAX_CONCURRENT_LOW_SPEED_DOWNLOAD=json_data_file_transfer_main_config["max_concurrent_low_speed_download"]
MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD=json_data_file_transfer_main_config["max_concurrent_high_speed_download"]
SLOW_SPEED_BREAK_DOWNLOAD_WHEN_SIZE_EXCEED=json_data_file_transfer_main_config["slow_speed_break_download_when_size_exceed"]

class HASH_TO_IP_CLASS:
    @staticmethod
    def netmask_handle(local_netmask,unique_ids,UNIQUE_ID_TO_IPS):
        """
        Handle when subnets are different
        """
        DIFFERENT_SUBNET_COMMUNICATION_ALLOWED=True

        same_mask=0
        different_mask=0

        same_mask_ids={}
        for unique_id in unique_ids:
            ip_n_netmask=UNIQUE_ID_TO_IPS[unique_id]
            if ip_n_netmask:
                ip,ip_netmask=ip_n_netmask
                if((ip_netmask and local_netmask==ip_netmask) or DIFFERENT_SUBNET_COMMUNICATION_ALLOWED):
                    same_mask+=1
                    same_mask_ids[unique_id]=ip
                else:
                    different_mask+=1

        if not different_mask and not DIFFERENT_SUBNET_COMMUNICATION_ALLOWED:
            log(f"Total {same_mask} ips are on same subnet")
            log(f"Total {different_mask} ips are on different subnet",1)
            log(f"Advice on switching to same subnet if (same subnet ips[{same_mask}]> different subnet ips[{different_mask}]), in leymans terms, maybe your organization has wifi and LAN so change it to LAN or wifi accordingly",1)

        return same_mask_ids

    @staticmethod    
    def live_and_correct_ips(local_netmask, unique_ids, UNIQUE_ID_TO_IPS,CACHE_ID_TO_IP):
        """
        Check live IPs and correct id_to_ip mapping using multiple threads with a maximum of 100 concurrent threads.
        """
        filtered_ips_n_speed = []
        same_subnet_ips = HASH_TO_IP_CLASS.netmask_handle(local_netmask, unique_ids, UNIQUE_ID_TO_IPS)

        UNIQUE_IP=set()
        
        def check_ip_thread(id, ip):
            result_live_ip_check=live_ip_checker(id, ip)
            if result_live_ip_check:
                filtered_ips_n_speed.append((ip,result_live_ip_check[1]))

        unique_id_ip=[]
        for id in same_subnet_ips:
            ip = same_subnet_ips[id]
            if ip in UNIQUE_IP:
                continue
            if ip in CACHE_ID_TO_IP:
                filtered_ips_n_speed.append((ip,CACHE_ID_TO_IP[ip]))
                UNIQUE_IP.add(ip)
                continue
            unique_id_ip.append((id,ip))
            UNIQUE_IP.add(ip)

        sem = threading.Semaphore(25)
        threads = []
        for id ,ip in unique_id_ip:
            sem.acquire()
            thread = threading.Thread(target=check_ip_thread, args=(id, ip))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        for ip,speed in filtered_ips_n_speed:
            CACHE_ID_TO_IP[ip]=speed

        # sort ip based on transfer speed
        filtered_ips_n_speed.sort(key=lambda x: x[1], reverse=True)
        unique_filtered_ips_n_speed = []
        unique_ip_helper_for_unique_filtered_ips_n_speed = set()
        for ip,speed in filtered_ips_n_speed:
            if ip not in unique_ip_helper_for_unique_filtered_ips_n_speed:
                unique_filtered_ips_n_speed.append((ip,speed))
                unique_ip_helper_for_unique_filtered_ips_n_speed.add(ip)
        return unique_filtered_ips_n_speed
            
    @staticmethod
    def HASHES_TO_IDS(hashes):
        UNIQUE_IDS=set()
        if not hashes:
            log("No hashes to download either server or clients having files are down",2)
            return
        for hash in hashes:
            unique_ids=hashes[hash]
            for unique_id in unique_ids:
                UNIQUE_IDS.add(unique_id)
        return list(UNIQUE_IDS)

    @staticmethod
    def hash_to_ip(hashes):
        """
        Convert hash to online IP
        """
        c_s_server_ip=get_ip_address(C_S_model_SERVER_ADDR)
        local_ip=get_my_connect_ip(c_s_server_ip)
        local_netmask=get_netmask(local_ip)

        # Call Server with hashes and get unique_ids
        HASH_TO_ID= fetch_unique_id_from_hashes(hashes)
        if not HASH_TO_ID:
            return None
        
        IDS=HASH_TO_IP_CLASS.HASHES_TO_IDS(HASH_TO_ID)

        # Call Server with unique_ids and get ips
        UNIQUE_ID_TO_IPS=get_ips_and_netmasks(IDS)
        if(not UNIQUE_ID_TO_IPS[0]):
            log("Fetching with server failed, unable to get UNIQUE_ID_TO_IPS",2)
            return {}
        else:
            UNIQUE_ID_TO_IPS=UNIQUE_ID_TO_IPS[1]
        
        CACHE_ID_TO_IP={}
        ALL_FILES_DOWNLOADABLE=True
        filtered_hash_to_ip_n_speed={}
        for hash in hashes:
            if hash==None:
                continue
            unique_ids=HASH_TO_ID[hash]
            filtered_ips_n_speed=HASH_TO_IP_CLASS.live_and_correct_ips(local_netmask,unique_ids,UNIQUE_ID_TO_IPS,CACHE_ID_TO_IP)
            filtered_hash_to_ip_n_speed[hash]=filtered_ips_n_speed
            if(not filtered_ips_n_speed):
                ALL_FILES_DOWNLOADABLE=False
                log(f"No client is up having file with hash {hash}",2)

        if not ALL_FILES_DOWNLOADABLE:
            log(f"You need to later redownload to complete remaining files or we can do automatic sheduling for redownload",2)
            log(f"Currently downloading files which are available",1)
        return filtered_hash_to_ip_n_speed

class DOWNLOAD_FILE_CLASS:
    @staticmethod
    def file_path_filter(file_paths):
        good_paths = []
        with open(CONFIG_FOLDER_LOCATION) as f:
            data = json.load(f)
        for value in data.values():
            good_paths.append(value["path"])

        all_path_good=True
        for good_path in good_paths:
            if("Premium" in good_path):
                continue
            good_path = os.path.realpath(good_path)
            for file_path in file_paths:
                file_path = os.path.realpath(file_path)
                # Check if file_path is a subdirectory or file within good_path
                if os.path.commonpath([good_path, file_path]) != good_path:
                    # reporting via threat report
                    log(f"{good_path} is not a subdirectory of {file_path}",2)
                    log(f"Reporting this to threat report",2)
                    all_path_good=False
                    break

        return all_path_good
    
    @staticmethod
    def dir_create(folder_path):
        """
        Create directory structure
        """
        os.makedirs(folder_path, exist_ok=True)
    
    @staticmethod
    def handle_download(file_paths, file_sizes, file_hashes,table_names):
        """
        Handle download
        """
        start_time=time.time()
        if not os.path.exists(TMP_DOWNLOAD_DIR):
            os.makedirs(TMP_DOWNLOAD_DIR)
        global MAX_CONCURRENT_DOWNLOAD_TO_SINGLE_IP
        global BREAK_DOWNLOAD_WHEN_SIZE_EXCEED
        global IP_LOCK_TAKEN_BY_BIG_FILE_DOWNLOAD
        global SIZE_AFTER_WHICH_FILE_IS_CONSIDERED_BIG
        global HIGH_SPEED_THRESHOLD
        global MAX_CONCURRENT_LOW_SPEED_DOWNLOAD
        global MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD
        global SLOW_SPEED_BREAK_DOWNLOAD_WHEN_SIZE_EXCEED

        file_info = [(file_path, int(file_size), file_hash, table_name) for file_path, file_size, file_hash, table_name in zip(file_paths, file_sizes, file_hashes, table_names) if file_hash]
        file_info = sorted(file_info, key=lambda x: x[1], reverse=True)
        if not file_info:
            log("NO File is with anyone who is up ,DOWNLOAD FAILED",2)
            return False
        
        TOTAL_SIZE = sum(file_size for _, file_size, _, _ in file_info)
        DOWNLOADED_SIZE = 0
        DOWNLOADED_FILE_PATHS=set()
        DOWNLOADED_SIZE_lock = threading.Lock()
        log(f"TOTAL_SIZE to download: {TOTAL_SIZE/(1024*1024):.3g} MB")

        if not file_info:
            log("No hashes found",2)
            return None
        
        ALL_IPS_N_SPEED=set()
        UNIQUE_IPS_helper_for_ALL_IPS_N_SPEED=set()
        ALL_IPS_N_SPEED_lock=threading.Lock()
        HIGH_SPEED_IPS=set()
        LOW_SPEED_IPS=set()
        HASH_TO_IP_N_SPEED=HASH_TO_IP_CLASS.hash_to_ip([file_hash for _, _, file_hash, _ in file_info])
        if not HASH_TO_IP_N_SPEED:
            return False
        HASH_TO_IP = {}
        FILE_TRIED_TIMES={}
        FILE_TRIED_TIMES_lock=threading.Lock()
        FILE_WAIT_BEFORE_RETRY={}
        FILE_WAIT_BEFORE_RETRY_lock=threading.Lock()
        FILE_RETRY_WAIT_TIME=0.1 #seconds

        for hash in HASH_TO_IP_N_SPEED:
            ips=[]
            speeds=[]
            for ip,speed in HASH_TO_IP_N_SPEED[hash]:
                ips.append(ip)
                speeds.append(speed)
                if ip not in UNIQUE_IPS_helper_for_ALL_IPS_N_SPEED:
                    ALL_IPS_N_SPEED.add((ip,speed))
                    UNIQUE_IPS_helper_for_ALL_IPS_N_SPEED.add(ip)
            HASH_TO_IP[hash]=ips

        big_file_info = []
        small_file_info = []
        log(f"Info of files to download: {file_info}")
        for file_path, file_size, file_hash,table_name in file_info:
            FILE_WAIT_BEFORE_RETRY[file_path]=time.time()
            if int(file_size) > SIZE_AFTER_WHICH_FILE_IS_CONSIDERED_BIG:
                big_file_info.append((file_path,file_hash,table_name,file_size))
                FILE_TRIED_TIMES[file_path]=10
            else:
                small_file_info.append((file_path,file_hash,table_name,file_size))
                FILE_TRIED_TIMES[file_path]=15
        if not (len(ALL_IPS_N_SPEED)):
            log("No client alive having any of the files",2)
            return False

        # Thread safe
        RETRY_DOWNLOADS=queue.Queue()

        TOTAL_SPEED=sum([speed for ip,speed in ALL_IPS_N_SPEED])+1e-9
        log(f"TOTAL_SPEED: {TOTAL_SPEED/(10**6):.5g} MBps  from {len(ALL_IPS_N_SPEED)} ips")

        ESTIMATED_TIME=TOTAL_SIZE/TOTAL_SPEED
        INITIAL_MAX_CONCURRENT_LOW_SPEED_DOWNLOAD=MAX_CONCURRENT_LOW_SPEED_DOWNLOAD
        INITIAL_MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD=MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD
        MAX_CONCURRENT_LOW_SPEED_DOWNLOAD_lock=threading.Lock()
        MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD_lock=threading.Lock()

        big_file_lock=threading.Lock()
        IP_LOCK_N_FAILURE = {}
        ip_lock_n_failure_lock=threading.Lock()
        map_high_speed_ip_usage={}
        map_high_speed_ip_usage_lock=threading.Lock()
        high_speed_priority_queue = []
        high_speed_priority_queue_lock=threading.Lock()
        times_high_speed_priority_queue_updated=0
        times_high_speed_priority_queue_updated_lock=threading.Lock()
        low_speed_priority_queue = []
        low_speed_priority_queue_lock=threading.Lock()
        times_low_speed_priority_queue_updated=0
        times_low_speed_priority_queue_updated_lock=threading.Lock()
        FAILED_DOWNLOADS=set()
        FAILED_DOWNLOAD_lock=threading.Lock()


        SUM_LOW_SPEEDS=0
        for ip,speed in ALL_IPS_N_SPEED:
            IP_LOCK_N_FAILURE[ip]=[MAX_CONCURRENT_DOWNLOAD_TO_SINGLE_IP,0]
            if speed>=HIGH_SPEED_THRESHOLD:
                heapq.heappush(high_speed_priority_queue,(-speed,1,ip))
                HIGH_SPEED_IPS.add(ip)
            else:
                heapq.heappush(low_speed_priority_queue,(-speed,1,ip))
                LOW_SPEED_IPS.add(ip)
                SUM_LOW_SPEEDS+=speed
        if len(low_speed_priority_queue):
            AVG_LOW_SPEEDS=SUM_LOW_SPEEDS/len(low_speed_priority_queue)
        else:
            AVG_LOW_SPEEDS=0.000001

        for _,file_hash,_,_ in big_file_info:
            if file_hash in HASH_TO_IP and HASH_TO_IP[file_hash]:
                for ip in HASH_TO_IP[file_hash]:
                    if ip in map_high_speed_ip_usage:
                        map_high_speed_ip_usage[ip]+=1
                    else:
                        map_high_speed_ip_usage[ip]=1

        if(not high_speed_priority_queue):
            log("No high speed ips found",1)
            log(f"Downloading with slow speed ips",1)
        else:
            log(f"Found {len(high_speed_priority_queue)} high speed ips")
            log(f"Found {len(low_speed_priority_queue)} low speed ips")
        LEN_high_speed_priority_queue=len(high_speed_priority_queue)


        def report_progress():
            downloaded = LOCKS.access_DOWNLOADED_SIZE(None,None,fetch=True)
            progress = downloaded / TOTAL_SIZE
            progress_percent = int(progress * 100)
            total_bar_length = int(progress*25)

            bar = ('#' * (total_bar_length) + '-' * ((25 - total_bar_length)))

            bar_color = 'green' if progress_percent >= 50 else 'yellow'
            percent_color = 'cyan'

            # Calculate estimated time remaining
            elapsed_time = time.time() - start_time
            estimated_total_time = elapsed_time / progress if progress > 0 else 0
            estimated_remaining_time = estimated_total_time - elapsed_time

            # Format estimated remaining time
            minutes = int(estimated_remaining_time // 60)
            seconds = int(estimated_remaining_time % 60)
            progress_str = f"Downloading: [{colored(bar, bar_color):<25}] {colored(progress_percent, percent_color)}%"
            estimated_time_str = f" ET: {minutes} min {seconds} sec"

            print('\r' + progress_str + estimated_time_str, end='')

        class LOCKS:
            def access_SEG_DONE_CNT(file_path,fetch=False):
                nonlocal SEG_DONE_CNT
                SEG_DONE_CNT_lock.acquire()
                if fetch:
                    if file_path in SEG_DONE_CNT:
                        SEG_DONE_CNT_lock.release()
                        return SEG_DONE_CNT[file_path]
                    else:
                        SEG_DONE_CNT_lock.release()
                        return 0
                if file_path:
                    if file_path in SEG_DONE_CNT:
                        SEG_DONE_CNT[file_path]+=1
                    else:
                        SEG_DONE_CNT[file_path]=1
                SEG_DONE_CNT_lock.release()
                return
                
            def access_FILE_WAIT_BEFORE_RETRY(file_path):
                nonlocal FILE_WAIT_BEFORE_RETRY
                FILE_WAIT_BEFORE_RETRY_lock.acquire()
                if file_path not in FILE_WAIT_BEFORE_RETRY:
                    FILE_WAIT_BEFORE_RETRY[file_path]=time.time()
                    FILE_WAIT_BEFORE_RETRY_lock.release()
                    return 0
                curr_time=time.time()
                file_last_time=FILE_WAIT_BEFORE_RETRY[file_path]
                FILE_WAIT_BEFORE_RETRY[file_path]=max(file_last_time,curr_time)+FILE_RETRY_WAIT_TIME
                FILE_WAIT_BEFORE_RETRY_lock.release()
                wait_time= max(0,FILE_RETRY_WAIT_TIME-(curr_time-file_last_time))
                return wait_time

            def access_FAILED_DOWNLOADS(file_path):
                nonlocal FAILED_DOWNLOADS
                nonlocal FAILED_DOWNLOAD_lock
                FAILED_DOWNLOAD_lock.acquire()
                FAILED_DOWNLOADS.add(file_path)
                FAILED_DOWNLOAD_lock.release()

            def access_FILE_TRIED_TIMES(file_path,check=False):
                nonlocal FILE_TRIED_TIMES
                FILE_TRIED_TIMES_lock.acquire()
                if file_path not in FILE_TRIED_TIMES:
                    FILE_TRIED_TIMES[file_path]=15
                if check:
                    if FILE_TRIED_TIMES[file_path]<=0:
                        FILE_TRIED_TIMES_lock.release()
                        return True
                    FILE_TRIED_TIMES_lock.release()
                    return False
                FILE_TRIED_TIMES[file_path]-=1
                FILE_TRIED_TIMES_lock.release()
                return True

            def heapify_high_speed_priority_queue():
                # instead of heapify rechecking the clients speed should be faster and better
                nonlocal times_high_speed_priority_queue_updated
                nonlocal INITIAL_MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD
                times_high_speed_priority_queue_updated_lock.acquire()
                times_high_speed_priority_queue_updated+=1
                if times_high_speed_priority_queue_updated>INITIAL_MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD:
                    high_speed_priority_queue_lock.acquire()
                    times_high_speed_priority_queue_updated=0
                    heapq.heapify(high_speed_priority_queue)
                    high_speed_priority_queue_lock.release()
                times_high_speed_priority_queue_updated_lock.release()

            def heapify_low_speed_priority_queue():
                # instead of heapify rechecking the clients speed should be faster and better
                nonlocal times_low_speed_priority_queue_updated
                nonlocal INITIAL_MAX_CONCURRENT_LOW_SPEED_DOWNLOAD
                times_low_speed_priority_queue_updated_lock.acquire()
                times_low_speed_priority_queue_updated+=1
                if times_low_speed_priority_queue_updated>INITIAL_MAX_CONCURRENT_LOW_SPEED_DOWNLOAD:
                    low_speed_priority_queue_lock.acquire()
                    times_low_speed_priority_queue_updated=0
                    heapq.heapify(low_speed_priority_queue)
                    low_speed_priority_queue_lock.release()
                times_low_speed_priority_queue_updated_lock.release()

            def access_DOWNLOADED_SIZE(file_path,inc_val,fetch=False):
                nonlocal DOWNLOADED_SIZE
                nonlocal DOWNLOADED_FILE_PATHS
                DOWNLOADED_SIZE_lock.acquire()
                if fetch:
                    val=DOWNLOADED_SIZE
                    DOWNLOADED_SIZE_lock.release()
                    return val
                if file_path not in DOWNLOADED_FILE_PATHS:
                    DOWNLOADED_FILE_PATHS.add(file_path)
                    DOWNLOADED_SIZE+=inc_val
                DOWNLOADED_SIZE_lock.release()
            
            def access_MAX_CONCURRENT_LOW_SPEED_DOWNLOAD(release=False,check=False,curr_cnt=False):
                global MAX_CONCURRENT_LOW_SPEED_DOWNLOAD
                MAX_CONCURRENT_LOW_SPEED_DOWNLOAD_lock.acquire()
                if curr_cnt:
                    val=MAX_CONCURRENT_LOW_SPEED_DOWNLOAD
                    MAX_CONCURRENT_LOW_SPEED_DOWNLOAD_lock.release()
                    return val
                if check:
                    if(MAX_CONCURRENT_LOW_SPEED_DOWNLOAD==INITIAL_MAX_CONCURRENT_LOW_SPEED_DOWNLOAD):
                        MAX_CONCURRENT_LOW_SPEED_DOWNLOAD_lock.release()
                        return True
                    MAX_CONCURRENT_LOW_SPEED_DOWNLOAD_lock.release()
                    return False
                if release:
                    MAX_CONCURRENT_LOW_SPEED_DOWNLOAD+=1
                    MAX_CONCURRENT_LOW_SPEED_DOWNLOAD_lock.release()
                    return
                if(MAX_CONCURRENT_LOW_SPEED_DOWNLOAD<=0):
                    MAX_CONCURRENT_LOW_SPEED_DOWNLOAD_lock.release()
                    return False
                MAX_CONCURRENT_LOW_SPEED_DOWNLOAD-=1
                MAX_CONCURRENT_LOW_SPEED_DOWNLOAD_lock.release()
                LOCKS.heapify_low_speed_priority_queue()
                return True
            
            def access_MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD(release=False,check=False,curr_cnt=False):
                global MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD
                MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD_lock.acquire()
                if curr_cnt:
                    val=MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD
                    MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD_lock.release()
                    return val
                if check:
                    if(MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD==INITIAL_MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD):
                        MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD_lock.release()
                        return True
                    MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD_lock.release()
                    return False
                if release:
                    MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD+=1
                    MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD_lock.release()
                    return
                if(MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD<=0):
                    MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD_lock.release()
                    return False
                MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD-=1
                MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD_lock.release()
                LOCKS.heapify_high_speed_priority_queue()
                return True
            
            def access_ALL_IPS_N_SPEED(ip_to_rem,speed=None,check=False,ips_check=False,is_ip_deleted=False):
                nonlocal ALL_IPS_N_SPEED
                ALL_IPS_N_SPEED_lock.acquire()
                if check:
                    if len(ALL_IPS_N_SPEED)==0:
                        ALL_IPS_N_SPEED_lock.release()
                        return True
                    ALL_IPS_N_SPEED_lock.release()
                    return False
                
                if is_ip_deleted:
                    if len(ALL_IPS_N_SPEED):
                        for ip,speed in ALL_IPS_N_SPEED:
                            if ip==is_ip_deleted:
                                ALL_IPS_N_SPEED_lock.release()
                                return False
                    ALL_IPS_N_SPEED_lock.release()
                    return True
                
                if ips_check:
                    no_ips_live=True
                    if len(ALL_IPS_N_SPEED):
                        for ip,speed in ALL_IPS_N_SPEED:
                            if ip in ips_check:
                                no_ips_live=False
                                break
                    ALL_IPS_N_SPEED_lock.release()
                    return no_ips_live

                if ip_to_rem:
                    for ip,speed in ALL_IPS_N_SPEED:
                        if ip==ip_to_rem:
                            ALL_IPS_N_SPEED.remove((ip,speed))
                            ALL_IPS_N_SPEED_lock.release()
                            return False
                ALL_IPS_N_SPEED_lock.release()
                return True
            
            def access_ip_lock_n_failure(ip,release_ip=None,failure=False):
                nonlocal IP_LOCK_N_FAILURE
                ip_lock_n_failure_lock.acquire()
                if release_ip:
                    if release_ip not in IP_LOCK_N_FAILURE.keys():
                        ip_lock_n_failure_lock.release()
                        return False
                    IP_LOCK_N_FAILURE[release_ip][0]+=1
                    if failure:
                        IP_LOCK_N_FAILURE[release_ip][1]+=1
                    cnt,failure=IP_LOCK_N_FAILURE[release_ip]
                    if(failure>3 or cnt<=0):
                        if(failure>3):
                            log(f"Removing ip {release_ip} from list because of too many failures",1)
                            LOCKS.access_ALL_IPS_N_SPEED(ip_to_rem=release_ip)
                        ip_lock_n_failure_lock.release()
                        return False
                    ip_lock_n_failure_lock.release()
                    return True
                if ip:
                    if ip not in IP_LOCK_N_FAILURE.keys():
                        ip_lock_n_failure_lock.release()
                        return False
                    cnt,failure=IP_LOCK_N_FAILURE[ip]
                    if cnt<=0:
                        ip_lock_n_failure_lock.release()
                        return False
                    IP_LOCK_N_FAILURE[ip][0]-=1
                    ip_lock_n_failure_lock.release()
                    return True
            
            def access_big_file():
                big_file_lock.acquire()
                big_file_lock.release()

            def access_map_high_speed_ip_usage(ips,check_free_ips=False):
                nonlocal map_high_speed_ip_usage
                map_high_speed_ip_usage_lock.acquire()
                if check_free_ips:
                    if not map_high_speed_ip_usage:
                        map_high_speed_ip_usage_lock.release()
                        return False
                    free_ip=[]
                    for check_free_ip in check_free_ips:
                        if check_free_ip not in map_high_speed_ip_usage:
                            free_ip.append(check_free_ip)
                    if len(free_ip):
                        map_high_speed_ip_usage_lock.release()
                        return free_ip
                    map_high_speed_ip_usage_lock.release()
                    return False
                if ips:
                    for ip in ips:
                        if ip not in map_high_speed_ip_usage:
                            continue
                        map_high_speed_ip_usage[ip]-=1
                        if(map_high_speed_ip_usage[ip]==0):
                            del map_high_speed_ip_usage[ip]
                map_high_speed_ip_usage_lock.release()

            def access_high_speed_priority_queue(ips,release_ip=None,failure=False):
                nonlocal high_speed_priority_queue
                high_speed_priority_queue_lock.acquire()
                if release_ip:
                    for i,(speed,usage,ip) in enumerate(high_speed_priority_queue):
                        if ip==release_ip:
                            updated_speed=speed*(usage/(usage-1))
                            high_speed_priority_queue[i]=(updated_speed,usage-1,ip)
                            LOCKS.access_ip_lock_n_failure(None,release_ip=ip,failure=failure)
                            high_speed_priority_queue_lock.release()
                            return
                    
                for i, (speed,usage,ip) in enumerate(high_speed_priority_queue):
                    if ip in ips:
                        if (not LOCKS.access_ip_lock_n_failure(ip)):
                            continue
                        updated_speed = speed * (usage / (usage + 1))
                        high_speed_priority_queue[i] = (updated_speed, usage + 1, ip)
                        high_speed_priority_queue_lock.release()
                        return True,ip
                high_speed_priority_queue_lock.release()

                no_live_ip_in_ips=True
                for ip in ips:
                    if not LOCKS.access_ALL_IPS_N_SPEED(None,is_ip_deleted=ip) and ip in HIGH_SPEED_IPS:
                        no_live_ip_in_ips=False
                        break
                return False,no_live_ip_in_ips

            def access_low_speed_priority_queue(ips,release_ip=None,failure=False):
                nonlocal low_speed_priority_queue
                low_speed_priority_queue_lock.acquire()
                if release_ip:
                    for i,(speed,usage,ip) in enumerate(low_speed_priority_queue):
                        if ip==release_ip:
                            updated_speed=speed*(usage/(usage-1))
                            low_speed_priority_queue[i]=(updated_speed,usage-1,ip)
                            LOCKS.access_ip_lock_n_failure(None,release_ip=ip,failure=failure)
                            low_speed_priority_queue_lock.release()
                            return

                for i, (speed,usage,ip) in enumerate(low_speed_priority_queue):
                    if ip in ips:
                        if((ip in map_high_speed_ip_usage)):
                            continue
                        if (not LOCKS.access_ip_lock_n_failure(ip)):
                            continue
                        updated_speed = speed * (usage / (usage + 1))
                        low_speed_priority_queue[i] = (updated_speed, usage + 1, ip)
                        low_speed_priority_queue_lock.release()
                        return True,ip
                low_speed_priority_queue_lock.release()
                no_live_ip_in_ips=True
                for ip in ips:
                    if not LOCKS.access_ALL_IPS_N_SPEED(None,is_ip_deleted=ip) and ip in LOW_SPEED_IPS:
                        no_live_ip_in_ips=False
                        break
                return False,no_live_ip_in_ips
                    
        def handle_big_files(file_path,file_hash,table_name,start_byte,end_byte):
            def segment_download(seg_file_path,file_hash,table_name,start_byte,end_byte):
                wait_time=LOCKS.access_FILE_WAIT_BEFORE_RETRY(seg_file_path)
                time.sleep(wait_time)
                LOCKS.access_FILE_TRIED_TIMES(seg_file_path)
                if LOCKS.access_FILE_TRIED_TIMES(seg_file_path,check=True):
                    if os.path.exists(seg_file_path):
                        log(f"File {seg_file_path} already exists")
                        LOCKS.access_SEG_DONE_CNT(file_path)
                        LOCKS.access_DOWNLOADED_SIZE(seg_file_path,end_byte-start_byte+1)
                        LOCKS.access_MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD(release=True)
                        report_progress()
                        return True
                    log(f"Unable to download {seg_file_path} tried too many times",1)
                    LOCKS.access_FAILED_DOWNLOADS(file_path)
                    return False
                if os.path.exists(seg_file_path):
                    log(f"File {seg_file_path} already exists")
                    LOCKS.access_SEG_DONE_CNT(file_path)
                    LOCKS.access_DOWNLOADED_SIZE(seg_file_path,end_byte-start_byte+1)
                    LOCKS.access_MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD(release=True)
                    report_progress()
                    return True

                res = False
                while not res:
                    res,ip=LOCKS.access_high_speed_priority_queue(HASH_TO_IP[file_hash])
                    if ip and not res:
                        LOCKS.access_MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD(release=True)
                        RETRY_DOWNLOADS.put((seg_file_path,file_hash,table_name,start_byte,end_byte))
                        return
                    time.sleep(1)
                if(res):
                    result= file_download(ip,file_hash,table_name,start_byte,end_byte)
                    LOCKS.access_MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD(release=True)
                    if result:
                        with open(seg_file_path,"wb") as f:
                            data=base64.b64decode(result)
                            f.write(data)
                        LOCKS.access_high_speed_priority_queue(HASH_TO_IP[file_hash],release_ip=ip)
                        LOCKS.access_SEG_DONE_CNT(file_path)
                        LOCKS.access_DOWNLOADED_SIZE(seg_file_path,end_byte-start_byte+1)
                        report_progress()
                    else:
                        log(f"Unable to download {file_hash} from {ip}",1)
                        log(f"Retrying {file_hash} from {ip}",1)
                        LOCKS.access_high_speed_priority_queue(None,release_ip=ip,failure=True)
                        RETRY_DOWNLOADS.put((seg_file_path,file_hash,table_name,end_byte-start_byte+1,start_byte,end_byte))
                else:
                    RETRY_DOWNLOADS.put((file_path,file_hash,table_name,end_byte-start_byte+1,start_byte,end_byte))

            threads=[]
            segments=[]

            seg_num=0
            for break_num in range(start_byte,end_byte+1,BREAK_DOWNLOAD_WHEN_SIZE_EXCEED):
                file_dir=TMP_DOWNLOAD_DIR
                seg_file_path=os.path.join(file_dir,(file_hash+"_"+str(seg_num)+".dat"))
                seg_end_byte=min(break_num+BREAK_DOWNLOAD_WHEN_SIZE_EXCEED-1,end_byte)
                while not LOCKS.access_MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD():
                    time.sleep(2)
                thread = threading.Thread(target=segment_download,args=(seg_file_path,file_hash,table_name,break_num,seg_end_byte))
                thread.start()
                threads.append(thread)
                segments.append(seg_file_path)
                seg_num+=1

            for thread in threads:
                thread.join()

            seg_total_done=LOCKS.access_SEG_DONE_CNT(file_path,fetch=True)
            if seg_total_done!=seg_num:
                log(f"Unable to download {file_hash}",1)
                log(f"Retrying {file_hash}",1)
                RETRY_DOWNLOADS.put((file_path,file_hash,table_name,file_size,start_byte,end_byte))
                return
            
            # merge segments
            with open(file_path,"wb") as f:
                for seg_path in segments:
                    try:
                        with open(seg_path,"rb") as seg_f:
                            f.write(seg_f.read())
                            if(seg_num>1):
                                os.remove(seg_path)
                    except:
                        RETRY_DOWNLOADS.put((file_path,file_hash,table_name,file_size,start_byte,end_byte))
                        return False
            return True
        
        def handle_small_files(file_path,file_hash,table_name,start_byte,end_byte):
            def small_file_segment_download(seg_file_path,file_hash,table_name,start_byte,end_byte):
                wait_time=LOCKS.access_FILE_WAIT_BEFORE_RETRY(seg_file_path)
                time.sleep(wait_time)
                LOCKS.access_FILE_TRIED_TIMES(seg_file_path)
                if LOCKS.access_FILE_TRIED_TIMES(seg_file_path,check=True):
                    if os.path.exists(seg_file_path):
                        log(f"File {seg_file_path} already exists")
                        LOCKS.access_SEG_DONE_CNT(file_path)
                        LOCKS.access_DOWNLOADED_SIZE(seg_file_path,end_byte-start_byte+1)
                        LOCKS.access_MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD(release=True)
                        report_progress()
                        return True
                    log(f"Unable to download {seg_file_path} tried too many times",1)
                    UNABLE_TO_DOWNLOAD_ATLEAST_ONE_FILE=True
                    LOCKS.access_FAILED_DOWNLOADS(seg_file_path)
                    return False
                if os.path.exists(seg_file_path):
                    log(f"File {seg_file_path} already exists")
                    LOCKS.access_DOWNLOADED_SIZE(seg_file_path,end_byte-start_byte+1)
                    LOCKS.access_MAX_CONCURRENT_LOW_SPEED_DOWNLOAD(release=True)
                    LOCKS.access_map_high_speed_ip_usage(HASH_TO_IP[file_hash])
                    report_progress()
                    LOCKS.access_SEG_DONE_CNT(file_path)
                    return True
                CHANGED_TO_HIGH_SPEED=False
                FORCE_HIGH_SPEED=True
                for ip in HASH_TO_IP[file_hash]:
                    if ip in LOW_SPEED_IPS:
                        FORCE_HIGH_SPEED=False
                        break
                accessible_ips=LOCKS.access_map_high_speed_ip_usage(None,check_free_ips=HASH_TO_IP[file_hash])
                if accessible_ips or FORCE_HIGH_SPEED:
                    CHANGED_TO_HIGH_SPEED=True
                    LOCKS.access_MAX_CONCURRENT_LOW_SPEED_DOWNLOAD(release=True)
                    LOCKS.access_MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD()
                    res = False
                    while not res:
                        res,ip=LOCKS.access_high_speed_priority_queue(HASH_TO_IP[file_hash])
                        if ip and not res:
                            LOCKS.access_MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD(release=True)
                            RETRY_DOWNLOADS.put((seg_file_path,file_hash,table_name,end_byte-start_byte+1,start_byte,end_byte))
                            return
                        time.sleep(1)
                else:
                    res = False
                    while not res:
                        res,ip=LOCKS.access_low_speed_priority_queue(HASH_TO_IP[file_hash])
                        if ip and not res:
                            LOCKS.access_MAX_CONCURRENT_LOW_SPEED_DOWNLOAD(release=True)
                            RETRY_DOWNLOADS.put((seg_file_path,file_hash,table_name,end_byte-start_byte+1,start_byte,end_byte))
                            return
                        time.sleep(0.1)
                if(res):
                    result= file_download(ip,file_hash,table_name,start_byte,end_byte)
                    LOCKS.access_MAX_CONCURRENT_LOW_SPEED_DOWNLOAD(release=True)
                    if result:
                        with open(seg_file_path,"wb") as f:
                            data=base64.b64decode(result)
                            f.write(data)
                        if CHANGED_TO_HIGH_SPEED:
                            LOCKS.access_high_speed_priority_queue(accessible_ips,release_ip=ip)
                        else:
                            LOCKS.access_low_speed_priority_queue(HASH_TO_IP[file_hash],release_ip=ip)
                        LOCKS.access_SEG_DONE_CNT(file_path)
                        LOCKS.access_DOWNLOADED_SIZE(seg_file_path,end_byte-start_byte+1)
                        report_progress()
                    else:
                        log(f"Unable to download {file_hash}",1)
                        log(f"Retrying {file_hash}",1)
                        if CHANGED_TO_HIGH_SPEED:
                            LOCKS.access_high_speed_priority_queue(None,release_ip=ip,failure=True)
                        else:
                            LOCKS.access_low_speed_priority_queue(HASH_TO_IP[file_hash],release_ip=ip,failure=True)
                        RETRY_DOWNLOADS.put((seg_file_path,file_hash,table_name,end_byte-start_byte+1,start_byte,end_byte))
                else:
                    RETRY_DOWNLOADS.put((seg_file_path,file_hash,table_name,end_byte-start_byte+1,start_byte,end_byte))
            report_progress()
            threads=[]
            segments=[]
            seg_num=0
            for break_num in range(start_byte,end_byte+1,SLOW_SPEED_BREAK_DOWNLOAD_WHEN_SIZE_EXCEED):
                file_dir=TMP_DOWNLOAD_DIR
                seg_file_path=os.path.join(file_dir,(file_hash+"_"+str(seg_num)+".dat"))
                seg_end_byte=min(break_num+SLOW_SPEED_BREAK_DOWNLOAD_WHEN_SIZE_EXCEED-1,end_byte)
                while not LOCKS.access_MAX_CONCURRENT_LOW_SPEED_DOWNLOAD():
                    time.sleep(0.1)
                thread = threading.Thread(target=small_file_segment_download,args=(seg_file_path,file_hash,table_name,break_num,seg_end_byte))
                thread.start()
                threads.append(thread)
                segments.append(seg_file_path)
                seg_num+=1

            for thread in threads:
                thread.join()
            
            seg_total_done=LOCKS.access_SEG_DONE_CNT(file_path,fetch=True)

            if seg_total_done!=seg_num:
                log(f"Unable to download {file_hash}",1)
                log(f"Retrying {file_hash}",1)
                RETRY_DOWNLOADS.put((file_path,file_hash,table_name,file_size,start_byte,end_byte))
                return        
            
            # merge segments
            with open (file_path,"wb") as f:
                for seg_path in segments:
                    try:
                        with open(seg_path,"rb") as seg_f:
                            f.write(seg_f.read()) 
                            if seg_num>1:
                                os.remove(seg_path)
                    except:
                        RETRY_DOWNLOADS.put((file_path,file_hash,table_name,file_size,start_byte,end_byte))
                        return False
            return True         

        def handle_thread(file_path,file_hash,table_name,file_size,start_byte=None,end_byte=None):
            wait_time=LOCKS.access_FILE_WAIT_BEFORE_RETRY(file_path)
            time.sleep(wait_time)
            LOCKS.access_FILE_TRIED_TIMES(file_path)
            if LOCKS.access_FILE_TRIED_TIMES(file_path,check=True):
                if(os.path.exists(file_path)):
                    log(f"File {file_path} already exists")
                    LOCKS.access_DOWNLOADED_SIZE(file_path,file_size)
                    if file_size > SIZE_AFTER_WHICH_FILE_IS_CONSIDERED_BIG:
                        LOCKS.access_map_high_speed_ip_usage(HASH_TO_IP[file_hash])
                    report_progress()
                    return True
                if file_size>SIZE_AFTER_WHICH_FILE_IS_CONSIDERED_BIG:
                    LOCKS.access_map_high_speed_ip_usage(HASH_TO_IP[file_hash])
                log(f"Unable to download {file_path} tried too many times",1)
                LOCKS.access_FAILED_DOWNLOADS(file_path)
                return False
            if(os.path.exists(file_path)):
                log(f"File {file_path} already exists")
                LOCKS.access_DOWNLOADED_SIZE(file_path,file_size)
                if file_size > SIZE_AFTER_WHICH_FILE_IS_CONSIDERED_BIG:
                    LOCKS.access_map_high_speed_ip_usage(HASH_TO_IP[file_hash])
                report_progress()
                return True
            if (LOCKS.access_ALL_IPS_N_SPEED(None,None,ips_check=HASH_TO_IP[file_hash])):
                log(f"Unable to download {file_hash} no ips available",2)
                LOCKS.access_FAILED_DOWNLOADS(file_path)
                return
            send_to_low_speed=False
            ips_len=len(HASH_TO_IP[file_hash])
            if((((file_size)/(AVG_LOW_SPEEDS*ips_len +1e-9))<(ESTIMATED_TIME/2)) and (LOCKS.access_MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD(curr_cnt=True)<=0)):
                send_to_low_speed=True
            if ((not len(small_file_info)) or((file_size>SIZE_AFTER_WHICH_FILE_IS_CONSIDERED_BIG) and LEN_high_speed_priority_queue and (not send_to_low_speed))):
                if start_byte and end_byte:
                    handle_big_files(file_path,file_hash,table_name,start_byte,end_byte)
                else:
                    handle_big_files(file_path,file_hash,table_name,0,file_size-1)
            else:
                if start_byte and end_byte:
                    handle_small_files(file_path,file_hash,table_name,start_byte,end_byte)
                else:
                    handle_small_files(file_path,file_hash,table_name,0,file_size-1)

        SEG_DONE_CNT={}
        SEG_DONE_CNT_lock=threading.Lock()
        log("Starting download.........................")
        # high speed downloads
        threads=[]
        if len(big_file_info):
            for file_path,file_hash,table_name,file_size in big_file_info:
                thread = threading.Thread(target=handle_thread,args=(file_path,file_hash,table_name,file_size,True))
                thread.start()
                threads.append(thread)

        # retry high speed downloads
        while not(RETRY_DOWNLOADS.empty()):
            file_path,file_hash,table_name,file_size,start_byte,end_byte = RETRY_DOWNLOADS.get()
            thread = threading.Thread(target=handle_thread,args=(file_path,file_hash,table_name,file_size,start_byte,end_byte))
            thread.start()
            threads.append(thread)

        if not len(LOW_SPEED_IPS):
            for thread in threads:
                thread.join()
            threads=[]

        # low speed downloads
        if len(small_file_info):
            for file_path,file_hash,table_name,file_size in small_file_info:
                thread = threading.Thread(target=handle_thread,args=(file_path,file_hash,table_name,file_size,False))
                thread.start()
                threads.append(thread)

        for thread in threads:
            thread.join()

        threads=[]
        while(not(RETRY_DOWNLOADS.empty()) and not(LOCKS.access_ALL_IPS_N_SPEED(None,None,check=True))):
            file_path,file_hash,table_name,file_size,start_byte,end_byte=RETRY_DOWNLOADS.get()
            thread = threading.Thread(target=handle_thread,args=(file_path,file_hash,table_name,file_size,start_byte,end_byte))
            thread.start()
            threads.append(thread)
            for thread in threads:
                thread.join()

        if len(FAILED_DOWNLOADS):
            log(f"Unable to download all files , following files are not downloaded {FAILED_DOWNLOADS}",2)
            log(f"Please rerun the download again or we can automatically shedule the download for you",2)
            log(f"Failed download can also mean that the node has deleted the file and not updated the server yet",1)
            return False
        elif not(RETRY_DOWNLOADS.empty()):
            file_paths=[]
            while not(RETRY_DOWNLOADS.empty()):
                file_path,file_hash,table_name,file_size,start_byte,end_byte = RETRY_DOWNLOADS.get()
                file_paths.append(file_path)
            log(f"Unable to download all files , following files are not downloaded {file_paths}",2)
            log(f"Please rerun the download again or we can automatically shedule the download for you",2) 
            log(f"Total time taken {time.time()-start_time} seconds",0) 
            log(f"Failed download can also mean that the node has deleted the file and not updated the server yet",1)
            return False
        else:
            bar = ('#' * (25) + '-' * ((25 - 25)))
            bar_color = 'green' if 100 >= 50 else 'yellow'
            percent_color = 'cyan'
            print(f"\nDownloading: [{colored(bar, bar_color):<25}] {colored(100, percent_color)}%")
            log("\nDownload complete")
            log(f"Downloaded {file_paths}",0)
            log(f"Total time taken {time.time()-start_time} seconds",0)
            
            # remove .tmp_download files
            tmp_downloads=[]
            for file in os.listdir(TMP_DOWNLOAD_DIR):
                if os.path.isfile(os.path.join(TMP_DOWNLOAD_DIR,file)):
                    tmp_downloads.append(os.path.join(TMP_DOWNLOAD_DIR,file))
            for _,_,file_hash,_ in file_info:
                for tmp_download in tmp_downloads:
                    if file_hash in tmp_download:
                        os.remove(tmp_download)
                        tmp_downloads.remove(tmp_download)
            return True
    
    @staticmethod
    def process_subdb(subdb_filename,table_name):
        """
        Create directory structure
        """
        subdb_dir=os.path.join(SUB_DB_PATH,subdb_filename)
        subdb_conn=sqlite3.connect(subdb_dir)
        subdb_table_name="subdb"
        subdb_cursor=subdb_conn.cursor()

        # fetch first row
        subdb_cursor.execute("SELECT * FROM subdb")
        row_data=subdb_cursor.fetchone()
        if(not row_data):
            log(f"Unable to fetch row_data from {subdb_filename}",2)
            return None
        
        file_paths=[]
        file_sizes=[]
        file_hashes=[]
        table_names=[]
        dir_paths=[]

        root_id=row_data[0]
        Total_files=0
        
        def tree_iterator(id):
            nonlocal Total_files
            subdb_cursor.execute(
                f"SELECT * FROM {subdb_table_name} WHERE id = ?;", (id,))

            row_data = subdb_cursor.fetchone()
            is_file=row_data[2]
            meta_data=json.loads(row_data[5])
            if is_file:
                file_paths.append(meta_data["Path"])
                file_sizes.append(meta_data["Size"])
                dir_paths.append(os.path.dirname(meta_data["Path"]))
                file_hashes.append(row_data[8])
                Total_files+=1
            else:
                file_paths.append(meta_data["Path"])
                dir_paths.append(meta_data["Path"])
                file_sizes.append(None)
                file_hashes.append(None)
            table_names.append(table_name)

            child_ids = row_data[4]
            if (child_ids is None):
                return
            child_ids = [int(x.strip())
                            for x in child_ids.split(",")]
            if len(child_ids) == 0:
                return

            for child_id in child_ids:
                tree_iterator(child_id)

        tree_iterator(root_id)
        subdb_conn.close()
        log(f"Downloading {Total_files} files using subdb {subdb_filename}",0)

        # Check if file_paths are within good_paths
        if(not DOWNLOAD_FILE_CLASS.file_path_filter(file_paths)):
            # Report to threat_report module
            log(f"File paths are not within good_paths",2)
            return None
        
        # Create directory structure
        for dir in dir_paths:
            DOWNLOAD_FILE_CLASS.dir_create(dir)

        if not Total_files:
            log(f"No files to download all were folders")
            log(f"Successfully created folder structure")
            os.remove(subdb_dir)
            return True

        # Handle file downloading
        res= DOWNLOAD_FILE_CLASS.handle_download(file_paths,file_sizes,file_hashes,table_names)
        if (res):
            os.remove(subdb_dir)
        
        return res
    
    @staticmethod
    def up_check(unique_id):
        """
        check single unique_id if it is up
        """
        unique_ids=[unique_id]
        CACHE_ID_TO_IP={}
        unique_id_to_ips=get_ips_and_netmasks(unique_ids)
        c_s_server_ip=get_ip_address(C_S_model_SERVER_ADDR)
        local_ip=get_my_connect_ip(c_s_server_ip)
        local_netmask=get_netmask(local_ip)
        ips_n_speeds=HASH_TO_IP_CLASS.live_and_correct_ips(local_netmask,unique_ids,unique_id_to_ips,CACHE_ID_TO_IP)
        if not len(ips_n_speeds):
            log(f"ip is not up for unique_id {unique_id}",2)
            return False,0
        speed=sum([speed for _,speed in ips_n_speeds])
        return True,speed

        
    @staticmethod
    def main(unique_id,lazy_file_hash,table_name):
        """
        Main function
        """

        # Download subdb
        result=subdb_downloader(unique_id,lazy_file_hash)

        if(not result):
            log(f"Unable to download subdb for unique_id {unique_id}, lazy_file_hash {lazy_file_hash}, table_name {table_name}",2)
            return False
        
        subdb_filename=result

        # Process subdb and download files
        res=DOWNLOAD_FILE_CLASS.process_subdb(subdb_filename,table_name)
        if res:
            log(f"Downloaded lazy_file_hash {lazy_file_hash} Successfully",0)
        else:
            log(f"Download lazy_file_hash {lazy_file_hash} Partially/Fully Failed",2)
            return False
        return True

        
if __name__ == '__main__':
    # DOWNLOAD_FILE_CLASS.main("dae9a489-a077-4bba-82de-3f0e6cde0288","79abf0609459c5bf1e6dcb5d124d16e5",table_name="Normal_Content_Main_Folder")
     DOWNLOAD_FILE_CLASS.main("a7561257-324c-4186-91ec-45b5e766753f","e4a3871c86f6042767abebff3c1623f3",table_name="Normal_Content_Main_Folder")
  
