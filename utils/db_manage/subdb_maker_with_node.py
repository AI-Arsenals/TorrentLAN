import os
import sqlite3
import json
import hashlib
import time
import platform
import datetime

SOFTWARE_DIR = os.getcwd()
DATABASE_DIR = "data/.db"
CONFIG_FOLDER_LOCATION = "configs/folder_locations.json"
CONFIG_IDENTITY = "configs/identity.json"
UNIQUE_ID = json.load(open(CONFIG_IDENTITY))["client_id"]

SUB_DB_PATH = "data/.db/sub_db"


def subdb_maker(unique_id, hash):
    with open(CONFIG_FOLDER_LOCATION) as f:
        data = json.load(f)

    subdb_filename = unique_id + "_" + hash
    if (os.path.exists(os.path.join(SUB_DB_PATH + subdb_filename))):
        return True
    for db in os.listdir(DATABASE_DIR):
        if (db == (unique_id+".db")):
            conn = sqlite3.connect(os.path.join(DATABASE_DIR, db))
            cursor = conn.cursor()

            for table_name in data:
                query = '''
                    SELECT * FROM {table_name} WHERE hash = ?;
                '''.format(table_name=table_name)

                cursor.execute(query, (hash,))
                result = cursor.fetchall()
                print(result)
                # id=result[0]

            conn.close()

    return False


if __name__ == "__main__":
    subdb_maker(UNIQUE_ID, "a")
