import sys
import os
import json
import importlib.util as import_util

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from utils.log.main import log
from utils.file_transfer.live_ip_check import live_checker

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


NODE_PORT=8890

C_S_model_SERVER_CONFIG="configs/server.json"
C_S_model_SERVER_ADDR=json.load(open(C_S_model_SERVER_CONFIG))["server_addr"]

def netmask_handle(local_netmask,unique_ids,UNIQUE_ID_TO_IPS):
    """
    Handle when subnets are different
    """
    DIFFERENT_SUBNET_COMMUNICATION_ALLOWED=True

    same_mask=0
    different_mask=0

    same_mask_ids={}

    for unique_id in unique_ids:
        ip,ip_netmask=unique_ids[unique_id]
        if(local_netmask==ip_netmask or DIFFERENT_SUBNET_COMMUNICATION_ALLOWED):
            same_mask+=1
            same_mask_ids[unique_id]=ip
        else:
            different_mask+=1

    log(f"Total {same_mask} ips are on same subnet")
    log(f"Total {different_mask} ips are on different subnet",1)
    log(f"Advice on switching to same subnet if (same subnet ips[{same_mask}]> different subnet ips[{different_mask}]), in leymans terms, maybe your organization has wifi and LAN so change it to LAN or wifi accordingly",1)

    return same_mask_ids

    
def live_and_correct_ips(local_netmask,unique_ids,UNIQUE_ID_TO_IPS):
    """
    Check live ips && correct id_to_ip mapping
    """
    filtered_ips=[]
    same_subnet_ips=netmask_handle(local_netmask,unique_ids,UNIQUE_ID_TO_IPS)
    for id in same_subnet_ips:
        ip=same_subnet_ips[id]
        if(live_checker(id,ip)):
            filtered_ips.append(ip)

    return filtered_ips
        

def HASHES_TO_IDS(hashes):
    UNIQUE_IDS=[]
    for hash in hashes:
        unique_ids=hashes[hash]
        for unique_id in unique_ids:
            UNIQUE_IDS.append(unique_id)
    return UNIQUE_IDS


def hash_to_ip(hashes):
    """
    Convert hash to online IP
    """
    c_s_server_ip=get_ip_address(C_S_model_SERVER_ADDR)
    local_ip=get_my_connect_ip(c_s_server_ip)
    local_netmask=get_netmask(local_ip)

    # Call Server with hashes and get unique_ids
    returned_hashes= {"hash1":["unique_id1","unique_id2"],"hash2":["unique_id3","unique_id4"]}
    IDS=HASHES_TO_IDS(returned_hashes)

    # Call Server with unique_ids and get ips
    # returned format {"unique_id1":["ip1","netmask1"],"unique_id2":["ip2","netmask2"],"unique_id3":["ip3","netmask3"],"unique_id4":["ip4","netmask4"]}
    UNIQUE_ID_TO_IPS=get_ips_and_netmasks(IDS)


    filtered_hash_to_uniqueid={}
    for hash in hashes:
        unique_ids=hashes[hash]
        filtered_hash_ips=live_and_correct_ips(local_netmask,unique_ids,UNIQUE_ID_TO_IPS)
        filtered_hash_to_uniqueid[hash]=filtered_hash_ips

    return filtered_hash_to_uniqueid

