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
CONFIG_IDENTITY = "configs/identity.json"
UNIQUE_ID = json.load(open(CONFIG_IDENTITY))["client_id"]


def childs(unique_id,lazy_file_hash):
    with open(CONFIG_FOLDER_LOCATION) as f:
        data = json.load(f)
    
    files=[]
    folders=[]

    for db in os.listdir(DATABASE_DIR):
        if(not os.path.isfile(os.path.join(DATABASE_DIR, db))):
            continue
        if db == (unique_id + ".db"):
            conn = sqlite3.connect(os.path.join(DATABASE_DIR, db))
            cursor = conn.cursor()

            for table_name in data:
                query = '''
                    SELECT * FROM {table_name} WHERE lazy_file_check_hash = ?;
                '''.format(table_name=table_name)

                cursor.execute(query, (lazy_file_hash,))
                result = cursor.fetchall()

                if not result:
                    return files,folders

                if result:
                    parent_id = result[0][0]
                    hash_value = result[0][8]

                    row_query = f"SELECT * FROM {table_name} WHERE id = ?;"
                    cursor.execute(row_query, (parent_id,))
                    row_data = cursor.fetchone()
                    child_ids = row_data[4]

                    if(child_ids is None):
                        return files,folders
                    
                    child_ids=[int(x.strip()) for x in child_ids.split(",")]
                    if len(child_ids) == 0:
                        return files,folders

                    for child_id in child_ids:
                        cursor.execute(row_query, (child_id,))
                        row_data = cursor.fetchone()
                        if row_data[2] == True:
                            files.append(row_data[2])
                        else:
                            folders.append(row_data[2])
                    conn.close()
                    
                    return files,folders
            conn.close()

    return False,False

if __name__ == "__main__":
    pass
