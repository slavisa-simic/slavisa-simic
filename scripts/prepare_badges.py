"""Cache genuine Shields.io badges so profile views do not depend on a badge server."""
from urllib.request import Request,urlopen
from urllib.parse import quote,urlencode
import hashlib,json
from profile_common import ROOT

BADGES=[('java','Java','openjdk','ED8B00'),('spring-boot','Spring Boot','springboot','6DB33F'),('react','React','react','61DAFB'),('typescript','TypeScript','typescript','3178C6'),('postgresql','PostgreSQL','postgresql','73A7D3'),('docker','Docker','docker','2496ED'),('unity','Unity','unity','FFFFFF'),('csharp','C#',None,None),('ui-toolkit','UI Toolkit','unity','FFFFFF'),('codex','OpenAI Codex',None,None)]

def main():
    out=ROOT/'assets/profile/badges';out.mkdir(parents=True,exist_ok=True);manifest={}
    for slug,name,logo,color in BADGES:
        options={'style':'flat-square'}
        if logo:options.update(logo=logo,logoColor=color)
        url='https://img.shields.io/badge/'+quote(name,safe='')+'-1a232e?'+urlencode(options)
        path=out/f'{slug}.svg'
        if not path.exists():
            with urlopen(Request(url,headers={'User-Agent':'slavisa-profile-badges'}),timeout=30) as r:data=r.read()
            if b'<svg' not in data:raise ValueError('Badge server did not return an SVG')
            path.write_bytes(data)
        manifest[slug]={'name':name,'url':url,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    (out/'provenance.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'Cached {len(BADGES)} Shields.io badges.')

if __name__=='__main__':main()
