import os
import json

def load_raw_favs(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_raw_favs(items, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return True

def add_new_favs(new_items, file_path):
    existing = load_raw_favs(file_path)
    existing_ids = {item["id"] for item in existing if "id" in item}
    
    truly_new = []
    for item in new_items:
        if item.get("id") not in existing_ids:
            existing.append(item)
            existing_ids.add(item.get("id"))
            truly_new.append(item)
            
    save_raw_favs(existing, file_path)
    return truly_new
