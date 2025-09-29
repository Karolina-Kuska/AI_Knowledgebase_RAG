
import json, os, hashlib
STATE_FILE = "storage/last_watermark.json"

def load_watermark():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE, "r", encoding="utf-8")).get("updated_at")
    return None

def save_watermark(dt: str):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    json.dump({"updated_at": dt}, open(STATE_FILE, "w", encoding="utf-8"))

def content_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()
