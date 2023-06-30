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


def db_search(search_bys, searchs):
    with open(CONFIG_FOLDER_LOCATION) as f:
        data = json.load(f)

    RESULTS = []

    for db in os.listdir(DATABASE_DIR):
        if not os.path.isfile(os.path.join(DATABASE_DIR, db)):
            continue
        if db == ".gitkeep" or db == "file_tree.db":
            continue
        try:
            conn = sqlite3.connect(os.path.join(DATABASE_DIR, db))
            cursor = conn.cursor()

            for table_name in data:
                query = '''
                    SELECT * FROM {table_name} WHERE {conditions};
                '''.format(table_name=table_name, conditions=' AND '.join(['{} LIKE ?'.format(search_by) for search_by in search_bys]))

                cursor.execute(query, ['%' + search + '%' for search in searchs])
                results = cursor.fetchall()
                RESULTS.extend(results)

            conn.close()
        except sqlite3.OperationalError as e:
            log(f"Error accessing database file: {os.path.join(DATABASE_DIR, db)}", 2)
            log(f"Error message: {str(e)}", 2)

    return RESULTS

if __name__ == "__main__":
    log(db_search(["name","unique_id"],["main","041279ea-3370-40a8-a094-e9cbb5a389f2"]))
