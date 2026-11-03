"""Package the native profile snapshot and its reproducible build/refresh sources."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from html.parser import HTMLParser
import hashlib
import json
import re
ROOT=Path(__file__).resolve().parents[1]

class Assets(HTMLParser):
    def __init__(self):super().__init__();self.paths=set()
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in ('src','srcset','href') and value.startswith('assets/'):self.paths.add(value)

def archive(destination,files):
    with ZipFile(destination,'w',ZIP_DEFLATED,compresslevel=9) as output:
        for file in sorted(set(files)):
            if file.is_file():output.write(file,file.relative_to(ROOT).as_posix())

def main():
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    parser=Assets();parser.feed((ROOT/'README.md').read_text(encoding='utf-8'))
    ready=[ROOT/'README.md',ROOT/'docs/SOURCES.md',ROOT/'assets/profile/icons/Devicon-LICENSE',ROOT/'assets/profile/icons/Simple-Icons-LICENSE',*[ROOT/p for p in parser.paths]]
    archive(out/'profile-ready.zip',ready)
    source=ready+[ROOT/p for p in ('.gitignore','.gitattributes','package.json','package-lock.json','requirements.txt')]
    for folder in ('config','src','scripts','docs','tests','design-system','.github'):
        source.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    source.extend(p for p in (ROOT/'assets/profile').rglob('*') if p.is_file() and 'build' not in p.relative_to(ROOT/'assets/profile').parts)
    source.extend(p for p in (ROOT/'assets/source/fonts').glob('*') if p.is_file() and not p.name.startswith('Oxanium'))
    source.append(ROOT/'assets/source/personal-logo.png')
    archive(out/'profile-source.zip',source)
    # Verify both archives are readable and that all README images are included.
    for name in ('profile-ready.zip','profile-source.zip'):
        with ZipFile(out/name) as result:
            assert result.testzip() is None
            assert parser.paths.issubset(set(result.namelist())),'Archive misses profile images'
    manifest={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.glob('*.zip'))}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
