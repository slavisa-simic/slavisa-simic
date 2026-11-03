"""Verify the exact supplied logos before generating the project carousel."""
from pathlib import Path
import hashlib
import json
from profile_common import CONFIG,SOURCE

def main():
    SOURCE.mkdir(parents=True,exist_ok=True);manifest={}
    for project in CONFIG['projects']:
        logo=Path(project['logo'])
        logo_path=SOURCE/logo.name
        if not logo_path.is_file():raise FileNotFoundError(f'Missing official project logo: {logo}')
        digest=hashlib.sha256(logo_path.read_bytes()).hexdigest()
        assert digest==project['logo_sha256'],f'Supplied logo has changed: {logo}'
        manifest[logo.name]={'source':f'User-supplied official {project["name"]} logo','sha256':digest}
    (SOURCE/'provenance.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'Verified {len(manifest)} unchanged official project logos.')
if __name__=='__main__':main()
