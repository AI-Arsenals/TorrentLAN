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

    # check if unique_id is in search_bys
    unique_id = False
    if "unique_id" in search_bys:
        index = search_bys.index("unique_id")
        unique_id = searchs[index]
        searchs.pop(index)
        search_bys.pop(index)

    for db in os.listdir(DATABASE_DIR):
        if not os.path.isfile(os.path.join(DATABASE_DIR, db)):
            continue
        if db == ".gitkeep" or db == "file_tree.db":
            continue
        if unique_id:
            if(db!=unique_id+".db"):
                continue
        try:
            conn = sqlite3.connect(os.path.join(DATABASE_DIR, db))
            cursor = conn.cursor()

            for table_name in data:
                exact_searchs = ["id", "is_file", "parent_id", "child_id", "lazy_file_check_hash", "unique_id", "hash"]
                rest_col = ["name","metadata"]

                conds = []
                bind_param = []
                for i in range(len(search_bys)):
                    if search_bys[i] in exact_searchs:
                        conds.append("{} = ?".format(search_bys[i]))
                        bind_param.append(searchs[i])
                    elif search_bys[i] in rest_col:
                        conds.append("{} LIKE ?".format(search_bys[i]))
                        bind_param.append('%' + searchs[i] + '%')

                query = f"SELECT * FROM {table_name} WHERE " + ' AND '.join(conds)
                cursor.execute(query, tuple(bind_param))
                results = cursor.fetchall()
                RESULTS.extend(results)

            conn.close()
            if unique_id:
                break
        except sqlite3.OperationalError as e:
            log(f"Error accessing database file: {os.path.join(DATABASE_DIR, db)}", 2)
            log(f"Error message: {str(e)}", 2)

    return RESULTS

if __name__ == "__main__":
    log(db_search(["id","unique_id"],[5,"041279ea-3370-40a8-a094-e9cbb5a389f2"]))
