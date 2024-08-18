import json

def update_json_file(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_json_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)