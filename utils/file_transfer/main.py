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
spec =import_util.spec_from_file_location("client_uniqueid_to_ip_fetch_c_s", module_path)
module =import_util.module_from_spec(spec)
spec.loader.exec_module(module)
get_ips_and_netmasks = getattr(module, "get_ips_and_netmasks")

module_path = "utils/tracker/client_ip_reg(c-s).py"
spec =import_util.spec_from_file_location("client_uniqueid_to_ip_fetch_c_s", module_path)
module =import_util.module_from_spec(spec)
spec.loader.exec_module(module)
get_my_connect_ip=getattr(module, "get_my_connect_ip")
get_netmask=getattr(module, "get_netmask")
get_ip_address=getattr(module, "get_ip_address")

module_path = "utils/file_transfer/fetch_unique_id_from_hashes(c-s).py"
spec =import_util.spec_from_file_location("client_uniqueid_to_ip_fetch_c_s", module_path)
module =import_util.module_from_spec(spec)
spec.loader.exec_module(module)
fetch_unique_id_from_hashes=getattr(module, "fetch_unique_id_from_hashes")

module_path = "utils/file_transfer/sub_db_downloader(c-s).py"
spec =import_util.spec_from_file_location("client_uniqueid_to_ip_fetch_c_s", module_path)
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
    def live_and_correct_ips(local_netmask, unique_ids, UNIQUE_ID_TO_IPS):
        """
        Check live IPs and correct id_to_ip mapping using multiple threads with a maximum of 100 concurrent threads.
        """
        filtered_ips_n_speed = []
        same_subnet_ips = HASH_TO_IP_CLASS.netmask_handle(local_netmask, unique_ids, UNIQUE_ID_TO_IPS)

        def check_ip_thread(id, ip):
            result_live_ip_check=live_ip_checker(id, ip)
            if result_live_ip_check:
                filtered_ips_n_speed.append((ip,result_live_ip_check[1]))
            sem.release()  # Release the semaphore

        sem = threading.Semaphore(100)
        threads = []
        for id in same_subnet_ips:
            ip = same_subnet_ips[id]
            sem.acquire()
            thread = threading.Thread(target=check_ip_thread, args=(id, ip))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        # sort ip based on transfer speed
        filtered_ips_n_speed.sort(key=lambda x: x[1], reverse=True)
        return filtered_ips_n_speed
            
    @staticmethod
    def HASHES_TO_IDS(hashes):
        UNIQUE_IDS=[]
        if not hashes:
            log("No hashes to download either server or clients having files are down",2)
            return
        for hash in hashes:
            unique_ids=hashes[hash]
            for unique_id in unique_ids:
                UNIQUE_IDS.append(unique_id)
        return UNIQUE_IDS

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
        IDS=HASH_TO_IP_CLASS.HASHES_TO_IDS(HASH_TO_ID)

        # Call Server with unique_ids and get ips
        UNIQUE_ID_TO_IPS=get_ips_and_netmasks(IDS)
        if(not UNIQUE_ID_TO_IPS[0]):
            log("Fetching with server failed, unable to get UNIQUE_ID_TO_IPS",2)
            return {}
        else:
            UNIQUE_ID_TO_IPS=UNIQUE_ID_TO_IPS[1]

        ALL_FILES_DOWNLOADABLE=True
        filtered_hash_to_ip_n_speed={}
        for hash in hashes:
            if hash==None:
                continue
            unique_ids=HASH_TO_ID[hash]
            filtered_ips_n_speed=HASH_TO_IP_CLASS.live_and_correct_ips(local_netmask,unique_ids,UNIQUE_ID_TO_IPS)
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
            good_path = os.path.abspath(good_path)
            for file_path in file_paths:
                file_path = os.path.abspath(file_path)
                # Check if file_path is a subdirectory or file within good_path
                if os.path.commonpath([good_path, file_path]) != good_path:
                    # reporting via threat report
                    log(f"{good_path} is not a subdirectory of {file_path}",2)
                    log(f"Reporting this to threat report",2)
                    all_path_good=False
                    break

        return all_path_good
    
    @staticmethod
    def dir_create(file_path):
        """
        Create directory structure
        """
        if not os.path.exists(file_path):
            os.makedirs(file_path)
    
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
        TOTAL_SIZE = sum(file_size for _, file_size, _, _ in file_info)
        DOWNLOADED_SIZE = 0
        DOWNLOADED_SIZE_lock = threading.Lock()
        log(f"TOTAL_SIZE to download: {TOTAL_SIZE/(1024*1024)} MB")
        big_file_info = []
        small_file_info = []
        log(f"Info of files to download: {file_info}")
        for file_path, file_size, file_hash,table_name in file_info:
            if int(file_size) > SIZE_AFTER_WHICH_FILE_IS_CONSIDERED_BIG:
                big_file_info.append((file_path,file_hash,table_name,file_size))
            else:
                small_file_info.append((file_path,file_hash,table_name,file_size))

        if not file_info:
            log("No hashes found",2)
            return None
        
        ALL_IPS_N_SPEED=set()
        ALL_IPS_N_SPEED_lock=threading.Lock()
        HASH_TO_IP_N_SPEED=HASH_TO_IP_CLASS.hash_to_ip(file_hashes)
        HASH_TO_IP = {}
        for hash in HASH_TO_IP_N_SPEED:
            ips=[]
            speeds=[]
            for ip,speed in HASH_TO_IP_N_SPEED[hash]:
                ips.append(ip)
                speeds.append(speed)
                ALL_IPS_N_SPEED.add((ip,speed))
            HASH_TO_IP[hash]=ips

        if not (len(ALL_IPS_N_SPEED)):
            log("No client alive having any of the files",2)
            return False

        RETRY_DOWNLOADS=[]
        TOTAL_SPEED=sum([speed for ip,speed in ALL_IPS_N_SPEED])+1e-9
        log(f"TOTAL_SPEED: {int(TOTAL_SPEED/(10**6))} MBps  from {len(ALL_IPS_N_SPEED)} ips")

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


        SUM_LOW_SPEEDS=0
        for ip,speed in ALL_IPS_N_SPEED:
            IP_LOCK_N_FAILURE[ip]=[MAX_CONCURRENT_DOWNLOAD_TO_SINGLE_IP,0]
            if speed>=HIGH_SPEED_THRESHOLD:
                heapq.heappush(high_speed_priority_queue,(-speed,1,ip))
            else:
                heapq.heappush(low_speed_priority_queue,(-speed,1,ip))
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
            downloaded = LOCKS.access_DOWNLOADED_SIZE(None,fetch=True)
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

            def access_DOWNLOADED_SIZE(inc_val,fetch=False):
                nonlocal DOWNLOADED_SIZE
                DOWNLOADED_SIZE_lock.acquire()
                if fetch:
                    val=DOWNLOADED_SIZE
                    DOWNLOADED_SIZE_lock.release()
                    return val
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
            
            def access_ALL_IPS_N_SPEED(ip_to_rem,speed=None,check=False,ips_check=False):
                nonlocal ALL_IPS_N_SPEED
                ALL_IPS_N_SPEED_lock.acquire()
                if check:
                    if len(ALL_IPS_N_SPEED)==0:
                        ALL_IPS_N_SPEED_lock.release()
                        return True
                    ALL_IPS_N_SPEED_lock.release()
                    return False
                
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
                return False,None

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
                return False,None
                    
        def handle_big_files(file_path,file_hash,table_name,start_byte,end_byte):
            def segment_download(seg_file_path,file_hash,table_name,start_byte,end_byte,seg_done):
                if os.path.exists(seg_file_path):
                    log(f"File {seg_file_path} already exists")
                    seg_done.put((seg_file_path,True))
                    LOCKS.access_DOWNLOADED_SIZE(end_byte-start_byte+1)
                    report_progress()
                    return True
            
                res,ip=LOCKS.access_high_speed_priority_queue(HASH_TO_IP[file_hash])
                if(res):
                    result= file_download(ip,file_hash,table_name,start_byte,end_byte)
                    if result:
                        with open(seg_file_path,"wb") as f:
                            data=base64.b64decode(result)
                            f.write(data)
                        LOCKS.access_high_speed_priority_queue(HASH_TO_IP[file_hash],release_ip=ip)
                        seg_done.put((seg_file_path,True))
                        LOCKS.access_DOWNLOADED_SIZE(end_byte-start_byte+1)
                        report_progress()
                    else:
                        log(f"Unable to download {file_hash} from {ip}",1)
                        log(f"Retrying {file_hash} from {ip}",1)
                        LOCKS.access_high_speed_priority_queue(None,release_ip=ip,failure=True)
                        RETRY_DOWNLOADS.append((seg_file_path,file_hash,table_name,file_size,0,file_size-1))
                        seg_done.put((seg_file_path,False))
                else:
                    RETRY_DOWNLOADS.append((file_path,file_hash,table_name,file_size,0,file_size-1))
                    seg_done.put((seg_file_path,False))

            threads=[]
            segments=[]

            # queue.Queue() is thread safe
            seg_done=queue.Queue()
            seg_num=0
            for break_num in range(start_byte,end_byte+1,BREAK_DOWNLOAD_WHEN_SIZE_EXCEED):
                file_dir=TMP_DOWNLOAD_DIR
                seg_file_path=os.path.join(file_dir,(file_hash+"_"+str(seg_num)+".dat"))
                seg_end_byte=min(break_num+BREAK_DOWNLOAD_WHEN_SIZE_EXCEED-1,end_byte)
                thread = threading.Thread(target=segment_download,args=(seg_file_path,file_hash,table_name,break_num,seg_end_byte,seg_done))
                thread.start()
                threads.append(thread)
                segments.append(seg_file_path)
                seg_num+=1

            for thread in threads:
                thread.join()

            seg_total_done=0
            while not seg_done.empty():
                _, done = seg_done.get()
                if done:
                    seg_total_done+=1

            if seg_total_done!=seg_num:
                log(f"Unable to download {file_hash}",1)
                log(f"Retrying {file_hash}",1)
                RETRY_DOWNLOADS.append((file_path,file_hash,table_name,file_size,0,file_size-1))
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
                        RETRY_DOWNLOADS.append((file_path,file_hash,table_name,file_size,0,file_size-1))
                        return False
            return True
        
        def handle_small_files(file_path,file_hash,table_name,start_byte,end_byte):
            def small_file_segment_download(file_path,file_hash,table_name,start_byte,end_byte,seg_done):
                if os.path.exists(file_path):
                    log(f"File {file_path} already exists")
                    LOCKS.access_DOWNLOADED_SIZE(end_byte-start_byte+1)
                    report_progress()
                    seg_done.put((file_path,True))
                    return True
                CHANGED_TO_HIGH_SPEED=False
                accessible_ips=LOCKS.access_map_high_speed_ip_usage(None,check_free_ips=HASH_TO_IP[file_hash])
                if accessible_ips:
                    CHANGED_TO_HIGH_SPEED=True
                    res,ip=LOCKS.access_high_speed_priority_queue(accessible_ips)
                else:
                    res,ip=LOCKS.access_low_speed_priority_queue(HASH_TO_IP[file_hash])
                if(res):
                    result= file_download(ip,file_hash,table_name,start_byte,end_byte)
                    if result:
                        with open(file_path,"wb") as f:
                            data=base64.b64decode(result)
                            f.write(data)
                        if CHANGED_TO_HIGH_SPEED:
                            LOCKS.access_high_speed_priority_queue(accessible_ips,release_ip=ip)
                        else:
                            LOCKS.access_low_speed_priority_queue(HASH_TO_IP[file_hash],release_ip=ip)
                        seg_done.put((file_path,True))
                        LOCKS.access_DOWNLOADED_SIZE(end_byte-start_byte+1)
                        report_progress()
                    else:
                        log(f"Unable to download {file_hash}",1)
                        log(f"Retrying {file_hash}",1)
                        if CHANGED_TO_HIGH_SPEED:
                            LOCKS.access_high_speed_priority_queue(None,release_ip=ip,failure=True)
                        else:
                            LOCKS.access_low_speed_priority_queue(HASH_TO_IP[file_hash],release_ip=ip,failure=True)
                        RETRY_DOWNLOADS.append((file_path,file_hash,table_name,file_size,0,file_size-1))
                        seg_done.put((file_path,False))
                else:
                    RETRY_DOWNLOADS.append((file_path,file_hash,table_name,file_size,0,file_size-1))
                    seg_done.put((file_path,False))

            report_progress()
            threads=[]
            segments=[]
            # queue.Queue() is thread safe
            seg_done=queue.Queue()
            seg_num=0
            for break_num in range(start_byte,end_byte+1,SLOW_SPEED_BREAK_DOWNLOAD_WHEN_SIZE_EXCEED):
                file_dir=TMP_DOWNLOAD_DIR
                seg_file_path=os.path.join(file_dir,(file_hash+"_"+str(seg_num)+".dat"))
                seg_end_byte=min(break_num+SLOW_SPEED_BREAK_DOWNLOAD_WHEN_SIZE_EXCEED-1,end_byte)
                thread = threading.Thread(target=small_file_segment_download,args=(seg_file_path,file_hash,table_name,break_num,seg_end_byte,seg_done))
                thread.start()
                threads.append(thread)
                segments.append(seg_file_path)
                seg_num+=1

            for thread in threads:
                thread.join()

            seg_total_done=0
            while not seg_done.empty():
                _, done = seg_done.get()
                if done:
                    seg_total_done+=1

            if seg_total_done!=seg_num:
                log(f"Unable to download {file_hash}",1)
                log(f"Retrying {file_hash}",1)
                RETRY_DOWNLOADS.append((file_path,file_hash,table_name,file_size,0,file_size-1))
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
                        RETRY_DOWNLOADS.append((file_path,file_hash,table_name,file_size,0,file_size-1))
                        return False

            return True         

        def handle_thread(file_path,file_hash,table_name,file_size,big_file=False):
            if(os.path.exists(file_path)):
                log(f"File {file_path} already exists")
                LOCKS.access_DOWNLOADED_SIZE(file_size)
                report_progress()
                return
            if (LOCKS.access_ALL_IPS_N_SPEED(None,None,ips_check=HASH_TO_IP[file_hash])):
                log(f"Unable to download {file_hash} no ips available",2)
                return
            send_to_low_speed=False
            ips_len=len(HASH_TO_IP[file_hash])
            if((((file_size)/(AVG_LOW_SPEEDS*ips_len +1e-9))<(ESTIMATED_TIME/2)) and (LOCKS.access_MAX_CONCURRENT_HIGH_SPEED_DOWNLOAD(curr_cnt=True)<=0)):
                send_to_low_speed=True
            if ((file_size>SIZE_AFTER_WHICH_FILE_IS_CONSIDERED_BIG) and LEN_high_speed_priority_queue and (not send_to_low_speed)):
                handle_big_files(file_path,file_hash,table_name,0,file_size-1)
            else:
                handle_small_files(file_path,file_hash,table_name,0,file_size-1)

        log("Starting download.........................")
        # high speed downloads
        threads=[]
        if len(big_file_info):
            for file_path,file_hash,table_name,file_size in big_file_info:
                thread = threading.Thread(target=handle_thread,args=(file_path,file_hash,table_name,file_size,True))
                thread.start()
                threads.append(thread)

        # retry high speed downloads
        if len(RETRY_DOWNLOADS):
            for file_path,file_hash,table_name,file_size,start_byte,end_byte in RETRY_DOWNLOADS:
                thread = threading.Thread(target=handle_thread,args=(file_path,file_hash,table_name,file_size,True))
                thread.start()
                threads.append(thread)

        # low speed downloads
        if len(small_file_info):
            for file_path,file_hash,table_name,file_size in small_file_info:
                thread = threading.Thread(target=handle_thread,args=(file_path,file_hash,table_name,file_size,False))
                thread.start()
                threads.append(thread)

        for thread in threads:
            thread.join()

        threads=[]
        while(RETRY_DOWNLOADS and not(LOCKS.access_ALL_IPS_N_SPEED(None,None,check=True))):
            file_path,file_hash,table_name,file_size,start_byte,end_byte=RETRY_DOWNLOADS.pop()
            thread = threading.Thread(target=handle_thread,args=(file_path,file_hash,table_name,file_size,True))
            thread.start()
            threads.append(thread)
            for thread in threads:
                thread.join()

        if len(RETRY_DOWNLOADS):
            file_paths=[file_path for file_path,_,_,_,_,_ in RETRY_DOWNLOADS]
            log(f"Unable to download all files , following files are not downloaded {RETRY_DOWNLOADS}",2)
            log(f"Please rerun the download again or we can automatically shedule the download for you",2)          
            return False
        else:
            bar = ('#' * (25) + '-' * ((25 - 25)))
            bar_color = 'green' if 100 >= 50 else 'yellow'
            percent_color = 'cyan'
            f"Downloading: [{colored(bar, bar_color):<25}] {colored(100, percent_color)}%"
            log("\nDownload complete")
            log(f"Downloaded {file_paths}",0)

            
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

        def tree_iterator(id):
            subdb_cursor.execute(
                f"SELECT * FROM {subdb_table_name} WHERE id = ?;", (id,))

            row_data = subdb_cursor.fetchone()
            is_file=row_data[2]
            meta_data=json.loads(row_data[5])
            if is_file:
                file_paths.append(meta_data["Path"])
                file_sizes.append(meta_data["Size"])
                file_hashes.append(row_data[8])
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
        log(f"Downloading {len(file_paths)-len(dir_paths)} files using subdb {subdb_filename}",0)

        # Check if file_paths are within good_paths
        if(not DOWNLOAD_FILE_CLASS.file_path_filter(file_paths)):
            # Report to threat_report module
            log(f"File paths are not within good_paths",2)
            return None
        
        # Create directory structure
        for dir in dir_paths:
            DOWNLOAD_FILE_CLASS.dir_create(dir)

        # Handle file downloading
        return DOWNLOAD_FILE_CLASS.handle_download(file_paths,file_sizes,file_hashes,table_names)
        
    @staticmethod
    def main(unique_id,lazy_file_hash,table_name):
        """
        Main function
        """

        # Download subdb
        result=subdb_downloader(unique_id,lazy_file_hash)

        if(not result):
            log(f"Unable to download subdb for {unique_id}",2)
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
    # DOWNLOAD_FILE_CLASS.main("5e7350ca-5dd7-40df-9ea5-b2ece85bc4da","50386c5157c9fc0cffab1d53a0e5e5e4",table_name="Normal_Content_Main_Folder")
     DOWNLOAD_FILE_CLASS.main("5e7350ca-5dd7-40df-9ea5-b2ece85bc4da","719c9b30e27ee56ea2c9733084980e3e",table_name="Normal_Content_Main_Folder")
  
