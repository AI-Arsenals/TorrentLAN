import os
import sqlite3
import json
import hashlib
import time
import platform

SOFTWARE_DIR = os.getcwd()
DATABASE_DIR = "./data/.db"
DB_NAME = "file_tree.db"
CONFIG_FOLDER_LOCATION = "configs/folder_locations.json"
CONFIG_IDENTITY = "configs/identity.json"
UNIQUE_ID = json.load(open(CONFIG_IDENTITY))["client_id"]
USER_NAME = json.load(open(CONFIG_IDENTITY))["user_name"]

def lazy_file_check_hash(path, date_modified):
    """Hash of path + date_modified"""
    hasher = hashlib.md5()
    hasher.update(path.encode('utf-8'))
    hasher.update(date_modified.encode('utf-8'))
    return hasher.hexdigest()

def hash_generator(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as file:
        buffer = file.read(65536)
        while len(buffer) > 0:
            hasher.update(buffer)
            buffer = file.read(65536)

    return hasher.hexdigest()


def get_metadata(file_path):
    metadata = {}
    file_stat = os.stat(file_path)

    # Non-sensitive metadata
    metadata['Path'] = file_path
    metadata['Size'] = file_stat.st_size
    metadata['Last Modified'] = time.ctime(file_stat.st_mtime)
    metadata['Created'] = time.ctime(file_stat.st_ctime)
    metadata['OS'] = platform.system()
    metadata['User Name'] = USER_NAME

    return metadata

def check_file_in_db(conn, lazy_file_hash, table_name):
    check_query = '''
        SELECT * FROM {table_name} WHERE lazy_file_check_hash = ?;
    '''
    check_query = check_query.format(table_name=table_name)
    cursor = conn.cursor()
    cursor.execute(check_query, (lazy_file_hash,))
    result = cursor.fetchall()
    cursor.close()
    return result

def create_connection():
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, DB_NAME))

    # Delete Previous Tables
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
    tables = cursor.fetchall()
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table[0]};")
    conn.commit()
    cursor.close()

    return conn


def create_table(conn, table_name):
    create_table_query = '''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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


def insert_item(conn, table_name, name, is_file, parent_id, child_id, metadata, lazy_file_check_hash, unique_id, hash_value):
    insert_query = '''
        INSERT INTO {table_name} (name, is_file, parent_id, child_id, metadata, lazy_file_check_hash, unique_id, hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    '''
    cursor = conn.cursor()
    insert_query = insert_query.format(table_name=table_name)
    cursor.execute(insert_query, (name, is_file, parent_id, child_id, json.dumps(metadata), lazy_file_check_hash, unique_id, hash_value))
    conn.commit()
    last_row_id = cursor.lastrowid
    cursor.close()
    return last_row_id


def insert_at_id(conn, table_name, insert_id, child_id):
    child_id=', '.join(map(str, child_id))
    print(f"Inserting {child_id} at {insert_id}")
    update_query = '''
        UPDATE {table_name}
        SET child_id = ?
        WHERE id = ?;
    '''
    cursor = conn.cursor()
    update_query = update_query.format(table_name=table_name)
    cursor.execute(update_query, (child_id, insert_id))
    conn.commit()
    cursor.close()


def process_folder(conn, table_name, path, parent_id=None):
    if os.path.isfile(path):
        return []
    child_ids = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        is_file = os.path.isfile(item_path)
        metadata = get_metadata(item_path)

        if is_file:
            lazy_file_hash = lazy_file_check_hash(item_path, metadata['Last Modified'])
            # check if in db
            result = check_file_in_db(conn, lazy_file_hash, table_name)
            if len(result) > 0:
                continue

            hash_value = hash_generator(item_path)
            item_id = insert_item(conn, table_name, item, 1, parent_id, None, metadata, lazy_file_hash, UNIQUE_ID, hash_value)
            child_ids.append(item_id)
        else:
            lazy_file_hash = lazy_file_check_hash(item_path, metadata['Last Modified'])
            item_id = insert_item(conn, table_name, item, 0, parent_id, None, metadata, lazy_file_hash, UNIQUE_ID, "")
            child_ids.append(item_id)
            child_id_vals = process_folder(conn, table_name, item_path, item_id)
            if len(child_id_vals) > 0:
                insert_at_id(conn, table_name, item_id, child_id_vals)
    print(f"Child IDs: {child_ids}")
    return child_ids




def main():
    with open(CONFIG_FOLDER_LOCATION) as f:
        data = json.load(f)
    
    conn = create_connection()
    for key, value in data.items():
        path=value
        name=key
        create_table(conn, name)

        # root folder
        item_id=insert_item(conn, name, "root", 0, None, None, {}, "", UNIQUE_ID, "")
        child_id_vals=process_folder(conn, name, path)
        insert_at_id(conn, name, item_id, child_id_vals)
        
    conn.close()

if __name__ == '__main__':
    main()
