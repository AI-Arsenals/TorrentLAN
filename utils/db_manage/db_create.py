import os
import sqlite3
import json
import hashlib
import time
import platform
import datetime
import sys

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..')))
from utils.log.main import log

DATABASE_DIR = "data/.db"
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
    result = cursor.fetchone()
    cursor.close()
    return result

def create_connection():
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, DB_NAME))

    # # Delete Previous Tables
    # cursor = conn.cursor()
    # cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
    # tables = cursor.fetchall()
    # for table in tables:
    #     cursor.execute(f"DROP TABLE IF EXISTS {table[0]};")
    # conn.commit()
    # cursor.close()

    return conn

def delete_a_table(table_name):
    conn=sqlite3.connect(os.path.join(DATABASE_DIR, DB_NAME))

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
            FOREIGN KEY (child_id) REFERENCES {table_name} (id),
            CONSTRAINT idx_hash UNIQUE (hash),
            CONSTRAINT idx_lazy_file_check_hash UNIQUE (lazy_file_check_hash)
        );
    '''
    create_table_query = create_table_query.format(table_name=table_name)
    conn.execute(create_table_query)


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

def full_row_update_at_id(conn, table_name, insert_id, name=None, is_file=None, parent_id=None, child_id=None, metadata=None, lazy_file_check_hash=None, unique_id=None, hash_value=None):
    if child_id:
        child_id = ', '.join(map(str, child_id))
    update_query = '''
        UPDATE {table_name}
        SET {set_clause}
        WHERE id = ?;
    '''
    set_clause_parts = []
    values = []

    if name is not None:
        set_clause_parts.append('name = ?')
        values.append(name)
    if is_file is not None:
        set_clause_parts.append('is_file = ?')
        values.append(is_file)
    if parent_id is not None:
        set_clause_parts.append('parent_id = ?')
        values.append(parent_id)
    if child_id is not None:
        set_clause_parts.append('child_id = ?')
        values.append(child_id)
    if metadata is not None:
        set_clause_parts.append('metadata = ?')
        values.append(json.dumps(metadata))
    if lazy_file_check_hash is not None:
        set_clause_parts.append('lazy_file_check_hash = ?')
        values.append(lazy_file_check_hash)
    if unique_id is not None:
        set_clause_parts.append('unique_id = ?')
        values.append(unique_id)
    if hash_value is not None:
        set_clause_parts.append('hash = ?')
        values.append(hash_value)

    set_clause = ', '.join(set_clause_parts)
    update_query = update_query.format(table_name=table_name, set_clause=set_clause)
    cursor = conn.cursor()
    values.append(insert_id)
    cursor.execute(update_query, tuple(values))
    conn.commit()
    cursor.close()

def update_child_at_id(conn, table_name, insert_at_id, child_id):
    child_id=', '.join(map(str, child_id))
    update_query = '''
        UPDATE {table_name}
        SET child_id = ?
        WHERE id = ?;
    '''
    cursor = conn.cursor()
    update_query = update_query.format(table_name=table_name)
    cursor.execute(update_query, (child_id, insert_at_id))
    conn.commit()
    cursor.close()

def update_parent_at_id(conn, table_name, insert_id, parent_id):
    update_query = '''
        UPDATE {table_name}
        SET parent_id = ?
        WHERE id = ?;
    '''
    cursor = conn.cursor()
    update_query = update_query.format(table_name=table_name)
    cursor.execute(update_query, (parent_id, insert_id))
    conn.commit()
    cursor.close()

def process_folder(conn, table_name, path, parent_id=None):
    if os.path.isfile(path):
        return []
    child_ids = []
    SIZE=0
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        is_file = os.path.isfile(item_path)
        metadata = get_metadata(item_path)

        if is_file:
            lazy_file_hash = lazy_file_check_hash(item_path, metadata['Last Modified'])
            # check if in db
            result = check_file_in_db(conn, lazy_file_hash, table_name)
            hash_value = hash_generator(item_path)
            SIZE+=metadata['Size']
            if result:
                item_id = result[0]
                update_parent_at_id(conn, table_name, item_id, parent_id)
                # # Full row update for more robustness instead on only parent_id_update
                # full_row_update_at_id(conn, table_name, item_id, None, is_file, parent_id, None, metadata, None, UNIQUE_ID, hash_value)
                child_ids.append(item_id)
                continue

            item_id = insert_item(conn, table_name, item, 1, parent_id, None, metadata, lazy_file_hash, UNIQUE_ID, hash_value)
            child_ids.append(item_id)
        else:
            lazy_file_hash = lazy_file_check_hash(item_path, metadata['Last Modified'])
            # check if in db
            result = check_file_in_db(conn, lazy_file_hash, table_name)
            if result:
                item_id = result[0]
                update_parent_at_id(conn, table_name, item_id, parent_id)
                # # Full row update for more robustness instead of only parent_id_update
                # full_row_update_at_id(conn, table_name, item_id, None, is_file, parent_id, None, metadata, None, UNIQUE_ID, None)

                child_ids.append(item_id)
            else:
                item_id = insert_item(conn, table_name, item, 0, parent_id, None, None, lazy_file_hash, UNIQUE_ID, "")
                child_ids.append(item_id)
            child_id_vals,child_size = process_folder(conn, table_name, item_path, item_id)
            SIZE+=child_size
            if len(child_id_vals) > 0:
                metadata['Size'] += child_size
                full_row_update_at_id(conn, table_name, item_id, None, None, None, child_id_vals, metadata, None, None, None)
            else:
                full_row_update_at_id(conn, table_name, item_id, None, None, None, None, metadata, None, None, None)
    return child_ids,SIZE

def remove_deleted_files(conn, table_name, path):
    IDS_TO_NOT_DELETE = []

    cursor = conn.cursor()
    def get_all_child_ids(conn, table_name, id):
        cursor.execute(f"SELECT child_id FROM {table_name} WHERE id = ?;", (id,))
        child_ids = cursor.fetchall()
        if len(child_ids) == 0:
            return
        child_ids=child_ids[0][0]
        if(child_ids is None):
            return
        child_ids=[int(x.strip()) for x in child_ids.split(",")]

        for child_id in child_ids:
            IDS_TO_NOT_DELETE.append(child_id)
            get_all_child_ids(conn, table_name, child_id)

    # ROOT NODE
    cursor.execute(f"SELECT id,child_id FROM {table_name} WHERE parent_id IS NULL;")
    root_ids = cursor.fetchall()
    IDS_TO_NOT_DELETE.append(root_ids[0][0])
    root_ids=root_ids[0][1]
    if(root_ids is None):
        return
    root_ids=[int(x.strip()) for x in root_ids.split(",")]
    
    for root_id in root_ids:
        IDS_TO_NOT_DELETE.append(root_id)
        get_all_child_ids(conn, table_name, root_id)

    # Remove all IDs not present in 'IDS_TO_NOT_DELETE'
    cursor.execute(f"SELECT id FROM {table_name};")
    all_ids = cursor.fetchall()
    all_ids = [x[0] for x in all_ids]
    cursor.close()

    ids_to_delete = list(set(all_ids) - set(IDS_TO_NOT_DELETE))

    cursor = conn.cursor()
    if ids_to_delete:
        for id in ids_to_delete:
            cursor.execute(f"DELETE FROM {table_name} WHERE id = ?;", (id,))
    cursor.close()

    conn.commit()


def main(FORCE_UPDATE=False):
    with open(CONFIG_FOLDER_LOCATION) as f:
        data = json.load(f)
    
    conn = create_connection()
    for key, value in data.items():
        update_date = datetime.datetime.strptime(value["update_date"], "%Y-%m-%d %H:%M:%S.%f")
        current_time = datetime.datetime.now()
        elapsed_time = current_time - update_date
        if elapsed_time.total_seconds() <= 24 * 60 * 60 and not FORCE_UPDATE:
            log(f"Skipping {key} as it was updated less than 24 hours ago",1)
            continue
        path = value["path"]
        name = key
        data[key]["update_date"] = str(datetime.datetime.now())
        # delete_a_table(name)
        create_table(conn, name)

        # root folder
        metadata=get_metadata(path)
        lazy_file_hash = lazy_file_check_hash(path, metadata['Last Modified'])

        # check if root in db
        query = f"SELECT id FROM {name} WHERE parent_id IS NULL;"
        cursor=conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        
        if len(result) > 0:
            item_id = result[0][0]
            full_row_update_at_id(conn, name, item_id,"root", 0, None, None, None, lazy_file_hash, UNIQUE_ID, "")
        else:
            item_id=insert_item(conn, name, "root", 0, None, None, None, lazy_file_hash, UNIQUE_ID, "")
        child_id_vals,child_size=process_folder(conn, name, path, item_id)
        metadata['Size'] += child_size
        full_row_update_at_id(conn, name, item_id, None, None, None, child_id_vals, metadata, None, None, None)

        # remove deleted files
        remove_deleted_files(conn, name, path)

        log(f"Updated {name} successfully")
        
    conn.close()
    with open(CONFIG_FOLDER_LOCATION, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':
    main(FORCE_UPDATE=True)
