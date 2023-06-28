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
SUB_DB_PATH = "data/.db/sub_db"

def subdb_create_table(conn, table_name):
    create_table_query = '''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER,
            name TEXT,
            is_file INTEGER,
            parent_id INTEGER,
            child_id TEXT,
            metadata TEXT,
            lazy_file_check_hash TEXT,
            unique_id TEXT,
            hash TEXT,
            FOREIGN KEY (parent_id) REFERENCES {table_name} (id),
            FOREIGN KEY (child_id) REFERENCES {table_name} (id)
        );
    '''
    formatted_query = create_table_query.format(table_name=table_name)
    conn.execute(formatted_query)

def subdb_maker(unique_id, lazy_file_hash, subdb_filename):
    if not os.path.exists(SUB_DB_PATH):
        os.mkdir(SUB_DB_PATH)
    with open(CONFIG_FOLDER_LOCATION) as f:
        data = json.load(f)

    if os.path.exists(os.path.join(SUB_DB_PATH, subdb_filename))  or db=="file_tree".db:
        return True
    for db in os.listdir(DATABASE_DIR):
        if (not os.path.isfile(os.path.join(DATABASE_DIR, db))):
            continue
        if db==".gitkeep":
            continue
        if db == (unique_id + ".db"):
            conn = sqlite3.connect(os.path.join(DATABASE_DIR, db))
            cursor = conn.cursor()

            for table_name in data:
                query = '''
                    SELECT * FROM {table_name} WHERE lazy_file_check_hash = ?;
                '''.format(table_name=table_name)

                cursor.execute(query, (lazy_file_hash,))
                result = cursor.fetchone()

                if result:
                    parent_id = result[0]
                    hash_value = result[8]
                    log(f"Creating subdb of {table_name} of row with lazy_file_hash {lazy_file_hash} and parent_id {parent_id} and hash {hash_value}")
                    conn_subdb = sqlite3.connect(
                        os.path.join(SUB_DB_PATH, subdb_filename))
                    subdb_create_table(conn_subdb, table_name="subdb")
                    cursor_subdb = conn_subdb.cursor()

                    def tree_iterator(id):
                        row_query = f"SELECT * FROM {table_name} WHERE id = ?;"
                        cursor.execute(row_query, (id,))
                        row_data = cursor.fetchone()

                        # add this row to subdb
                        insert_query = f"""INSERT INTO {"subdb"} (id,name, is_file, parent_id, child_id, metadata, lazy_file_check_hash, unique_id, hash)
        VALUES (?,?, ?, ?, ?, ?, ?, ?, ?);"""
                        cursor_subdb.execute(insert_query, row_data)

                        child_ids = row_data[4]
                        if (child_ids is None):
                            return
                        child_ids = [int(x.strip())
                                     for x in child_ids.split(",")]
                        if len(child_ids) == 0:
                            return

                        for child_id in child_ids:
                            tree_iterator(child_id)

                    tree_iterator(parent_id)

                    conn_subdb.commit()
                    conn_subdb.close()
                    conn.close()

                    return True

            conn.close()

    return False


if __name__ == "__main__":
    lazy_file_hash = "7e31a3f574a4efed49bd0f3e565ac73d"
    UNIQUE_ID="5e7350ca-5dd7-40df-9ea5-b2ece85bc4da"
    subdb_maker(UNIQUE_ID, lazy_file_hash,
                subdb_filename=UNIQUE_ID + "_" + lazy_file_hash + ".db")
