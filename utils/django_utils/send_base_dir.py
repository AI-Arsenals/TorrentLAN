import json
CONFIG="configs/base_dir.json"

def get_base_dir():
    with open(CONFIG, "r") as f:
        js_data=json.load(f)
        BASE_DIR=js_data["BASE_DIR"]
    return BASE_DIR

if __name__=='__main__':
    print(get_base_dir())