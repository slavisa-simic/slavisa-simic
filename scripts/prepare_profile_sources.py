"""Cache the user's actual project headers and screenshots without changing the projects."""
from urllib.request import Request,urlopen
from pathlib import Path
import hashlib
import json
from profile_common import CONFIG,SOURCE

def main():
    SOURCE.mkdir(parents=True,exist_ok=True);manifest={}
    for project in CONFIG['projects']:
        for kind,url in project['sources'].items():
            extension=Path(url).suffix
            destination=SOURCE/f"{project['id']}-{kind}{extension}"
            if not destination.exists():
                with urlopen(Request(url,headers={'User-Agent':'slavisa-profile-source-cache'}),timeout=30) as response:destination.write_bytes(response.read())
            manifest[destination.name]={'source':url,'sha256':hashlib.sha256(destination.read_bytes()).hexdigest()}
    (SOURCE/'provenance.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(f'Prepared {len(manifest)} original project assets.')
if __name__=='__main__':main()
