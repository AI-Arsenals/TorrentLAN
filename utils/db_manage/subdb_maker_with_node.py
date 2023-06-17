import os
import sqlite3
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from utils.log.main import log
from utils.db_manage.db_create import create_table

SOFTWARE_DIR = os.getcwd()
DATABASE_DIR = "data/.db"
CONFIG_FOLDER_LOCATION = "configs/folder_locations.json"
CONFIG_IDENTITY = "configs/identity.json"
UNIQUE_ID = json.load(open(CONFIG_IDENTITY))["client_id"]

SUB_DB_PATH = "data/.db/sub_db"


def subdb_maker(unique_id, lazy_file_hash):
    if not os.path.exists(SUB_DB_PATH):
        os.mkdir(SUB_DB_PATH)
    with open(CONFIG_FOLDER_LOCATION) as f:
        data = json.load(f)

    subdb_filename = unique_id + "_" + lazy_file_hash + ".db"
    if os.path.exists(os.path.join(SUB_DB_PATH, subdb_filename)):
        return True
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

                if result:
                    parent_id = result[0][0]
                    hash_value = result[0][8]
                    log(f"Creating subdb of {table_name} of row with lazy_file_hash {lazy_file_hash} and parent_id {parent_id} and hash {hash_value}")
                    conn_subdb = sqlite3.connect(os.path.join(SUB_DB_PATH, subdb_filename))
                    create_table(conn_subdb, table_name="subdb")
                    cursor_subdb = conn_subdb.cursor()

                    def tree_iterator(id):
                        cursor.execute(f"SELECT child_id FROM {table_name} WHERE id = ?;", (id,))

                        # add this row to subdb
                        row_query = f"SELECT * FROM {table_name} WHERE id = ?;"
                        cursor.execute(row_query, (id,))
                        row_data = cursor.fetchone()
                        insert_query = f"INSERT INTO subdb VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"
                        cursor_subdb.execute(insert_query, row_data)

                        child_ids = row_data[4]
                        if(child_ids is None):
                            return
                        child_ids=[int(x.strip()) for x in child_ids.split(",")]
                        if len(child_ids) == 0:
                            return

                        for child_id in child_ids:
                            print(child_id)
                            tree_iterator(child_id)

                    tree_iterator(parent_id)

                    conn_subdb.commit()
                    conn_subdb.close()
                    conn.close()
                    
                    return True

            conn.close()

    return False


if __name__ == "__main__":
    subdb_maker(UNIQUE_ID, 'e328b5a31bef54961fca37563abe32cd')
