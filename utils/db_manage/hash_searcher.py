import os
import sqlite3
import json
import sys

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..')))
from utils.log.main import log

SOFTWARE_DIR = os.getcwd()
DATABASE_DIR = "data/.db"
CONFIG_FOLDER_LOCATION = "configs/folder_locations.json"


def hash_list_searcher(hashes):
    with open(CONFIG_FOLDER_LOCATION) as f:
        data = json.load(f)

    MAX_IDS_FORINFO=0
    HASH_TO_UNIQUE_IDS = {}
    for hash in hashes:
        HASH_TO_UNIQUE_IDS[hash] = set()
        
    for db in os.listdir(DATABASE_DIR):
        if(not os.path.isfile(os.path.join(DATABASE_DIR, db))):
            continue
        if db==".gitkeep":
            continue
        try:
            conn = sqlite3.connect(os.path.join(DATABASE_DIR, db))
            cursor = conn.cursor()

            for table_name in data:
                for hash in hashes:
                    query = '''
                        SELECT * FROM {table_name} WHERE hash = ?;
                    '''.format(table_name=table_name)

                    cursor.execute(query, (hash,))
                    results = cursor.fetchall()

                    for result in results:
                        HASH_TO_UNIQUE_IDS[hash].add(result[7])

            conn.close()
        except sqlite3.OperationalError as e:
            log(f"Error accessing database file: {os.path.join(DATABASE_DIR, db)}",2)
            log(f"Error message: {str(e)}",2)
            
    for hash_to_unique_ids in HASH_TO_UNIQUE_IDS:
        # convert to list
        HASH_TO_UNIQUE_IDS[hash_to_unique_ids] = list(HASH_TO_UNIQUE_IDS[hash_to_unique_ids])
        if len(HASH_TO_UNIQUE_IDS[hash_to_unique_ids]) > MAX_IDS_FORINFO:
            MAX_IDS_FORINFO = len(HASH_TO_UNIQUE_IDS[hash_to_unique_ids])

    log(f"Found max {MAX_IDS_FORINFO} unique ids for a single list search")
    return HASH_TO_UNIQUE_IDS

if __name__ == "__main__":
    log(hash_list_searcher(["2237ebf0d304cc26b9a2537c515a6b8e888c00f628e099e6e3f408beec89e11b"]))
