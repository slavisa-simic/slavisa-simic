from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
CONFIG=json.loads((ROOT/'config/profile.json').read_text(encoding='utf-8'))
OUT=ROOT/'assets/profile'
MEDIA=OUT/'generated'
SOURCE=OUT/'source'

def write_if_changed(path,content):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.read_text(encoding='utf-8')==content:return False
    path.write_text(content,encoding='utf-8',newline='\n');return True
