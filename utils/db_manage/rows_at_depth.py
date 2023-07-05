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


def rows_at_depth(depth, folder_name=None):
    with open(CONFIG_FOLDER_LOCATION) as f:
        data = json.load(f)

    if depth>1 and folder_name==None:
        return False,False

    Size_map = {}
    if depth == 0 or depth == 1:
        files = set()
        folders = set()
    else:
        files = []
        folders = []

    for db in os.listdir(DATABASE_DIR):
        if (not os.path.isfile(os.path.join(DATABASE_DIR, db))):
            continue
        if db==".gitkeep" or db=="file_tree.db":
            continue
        conn = sqlite3.connect(os.path.join(DATABASE_DIR, db))
        cursor = conn.cursor()

        for table_name in data:
            query = '''
                SELECT * FROM {table_name} WHERE parent_id IS NULL;
            '''.format(table_name=table_name)

            cursor.execute(query)
            result = cursor.fetchone()

            if result:
                if depth == 0:
                    files.add((-1, table_name, 0, None,
                              None, None, None, None, None))
                    metadata = json.loads(result[5])
                    if table_name in Size_map:
                        Size_map[table_name] += int(metadata["Size"])
                    else:
                        Size_map[table_name] = int(metadata["Size"])
                    continue

                child_ids = result[4]
                parent_id = result[0]
                parent_name=None
                

                if (child_ids is None):
                    continue

                child_ids = [int(x.strip()) for x in child_ids.split(",")]
                if len(child_ids) == 0:
                    continue

                depther=0
                def tree_iterator(id, depther,parent_name):
                    row_query = f"SELECT * FROM {table_name} WHERE id = ?;"
                    cursor.execute(row_query, (id,))
                    row_data = cursor.fetchone()


                    if depth == 1 and depther==1:
                        if row_data[2] == 1:
                            files.add((-2, row_data[1], 1, None,
                                        None, None, None, None, None))
                            metadata = json.loads(result[5])
                            if table_name in Size_map:
                                Size_map[row_data[1]] += int(metadata["Size"])
                            else:
                                Size_map[row_data[1]] = int(metadata["Size"])
                        else:
                            folders.add((-2, row_data[1], 0, None,
                                        None, None, None, None, None))
                            metadata = json.loads(result[5])
                            if table_name in Size_map:
                                Size_map[row_data[1]] += int(metadata["Size"])
                            else:
                                Size_map[row_data[1]] = int(metadata["Size"])
                        return

                    if depth == depther:
                        if parent_name==folder_name:
                            if row_data[2]==1:
                                files.append(row_data)
                            else:
                                folders.append(row_data)
                        return
                        
                    else:
                        child_ids = row_data[4]
                        if (child_ids is None):
                            return
                        child_ids = [int(x.strip())
                                    for x in child_ids.split(",")]
                        if len(child_ids) == 0:
                            return
                        for child_id in child_ids:
                            depther+=1
                            tree_iterator(child_id,depther,row_data[1])
                            depther-=1
                            
                tree_iterator(parent_id,depther,parent_name)

        conn.close()

    print(Size_map)
    if depth == 0 or depth == 1:
        files=list(files)
        folders=list(folders)
        for i, file in enumerate(files):
            metadata = {}
            metadata["Size"] = Size_map[file[1]]
            files[i] = list(file)
            files[i][5] = metadata
            files[i] = tuple(files[i])
        
        for i, folder in enumerate(folders):
            metadata = {}
            metadata["Size"] = Size_map[folder[1]]
            folders[i] = list(folder)
            folders[i][5] = metadata
            folders[i] = tuple(folders[i])

    return files, folders


if __name__ == "__main__":
    log(rows_at_depth(3,"Game1"))