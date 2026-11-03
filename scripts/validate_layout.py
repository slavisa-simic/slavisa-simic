"""Check source integrity, real decoded GIF frames, geometry, content, and README paths."""
from pathlib import Path
from contextlib import ExitStack
from html.parser import HTMLParser
from html import unescape
import argparse
import hashlib
import json
import math
import re
from urllib.request import Request,urlopen
from urllib.parse import urldefrag
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image
from generate_animations import CFG,OUT,ROOT,Film

class Markup(HTMLParser):
    def __init__(self): super().__init__();self.assets=set();self.links=set();self.images=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        assert tag not in ('script','style','iframe','canvas','map','svg'),f'Unsupported README tag: {tag}'
        assert 'style' not in attrs and 'class' not in attrs,'README contains unsupported styling'
        for name in ('src','srcset'):
            if name in attrs:self.assets.add(attrs[name])
        if 'href' in attrs:self.links.add(attrs['href'])
        if tag=='img':
            self.images+=1;assert attrs.get('alt'),'Image is missing alt text'

class Track:
    def __init__(self,image):self.image=image;self.index=0;self.until=image.info['duration']
    def at(self,time):
        while time>=self.until:
            self.index+=1;self.image.seek(self.index);self.until+=self.image.info['duration']
        return self.image.convert('RGB')

def check_url(url):
    with urlopen(Request(url,method='HEAD',headers={'User-Agent':'engineering-blueprint-link-check'}),timeout=25) as response:
        assert response.status==200,f'{url}: {response.status}'
        return {'url':url,'status':response.status,'resolved':response.url}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check-links',action='store_true');args=parser.parse_args()
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    markup=Markup();markup.feed(readme)
    assert markup.assets,'No profile assets'
    for relative in markup.assets:
        assert not relative.startswith(('http:','https:','data:')),'Profile depends on a remote image service'
        assert (ROOT/relative).is_file(),f'Missing asset: {relative}'
    skills=readme.split('## Personal skills\n')[1].split('\n## ')[0]
    assert not re.search(r'Unity|C#|game development',skills,re.I),'Unsupported personal game-development claim'
    assert '## AI Development Tools\n\n**OpenAI Codex**' in readme
    assert 'AI development case study' in readme
    assert 'game systems' not in readme.lower()
    sources=json.loads((OUT/'source-manifest.json').read_text(encoding='utf-8'))
    for relative,digest in sources.items():assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,f'Source changed: {relative}'
    assert CFG['panels'][0]['start']==0 and CFG['panels'][-1]['end']==1
    for left,right in zip(CFG['panels'],CFG['panels'][1:]):assert left['end']==right['start'],'Partition gap'
    report={'status':'passed','local_images':len(markup.assets),'source_files':len(sources),'variants':{}}
    for variant in ('desktop','mobile'):
        film=Film(variant);target=OUT/variant
        with ExitStack() as stack:
            files=[stack.enter_context(Image.open(target/'network.gif'))]
            files += [stack.enter_context(Image.open(target/f"{p['id']}.gif")) for p in CFG['panels']]
            durations=[]
            for image in files:
                assert image.info.get('loop')==0,'GIF does not loop forever'
                total=0
                for index in range(image.n_frames):image.seek(index);total+=image.info['duration']
                assert total==CFG['animation']['duration_ms'],'GIF timing mismatch'
                image.seek(0);durations.append(total)
            tracks=[Track(image) for image in files]
            first=None;last=None;max_delta=0;previous=None;max_edge_change=0;frames=0
            for time in range(0,CFG['animation']['duration_ms'],CFG['animation']['frame_ms']):
                full=np.array(tracks[0].at(time));combined=np.concatenate([np.array(t.at(time)) for t in tracks[1:]],axis=1)
                assert np.array_equal(full,combined),f'Decoded GIF crop mismatch at {variant}:{time}'
                if first is None:first=full.copy()
                for cut in film.cuts:
                    band=CFG['animation']['boundary_freeze']
                    change=int(np.max(np.abs(full[:,cut-band:cut+band].astype(int)-first[:,cut-band:cut+band].astype(int))))
                    max_edge_change=max(max_edge_change,change)
                if previous is not None:max_delta=max(max_delta,float(np.abs(full.astype(float)-previous).mean()))
                previous=full.astype(float);last=full;frames+=1
            assert max_edge_change==0,'Animated edge pixels could expose playback drift'
            loop_delta=float(np.abs(first.astype(float)-last.astype(float)).mean())
            assert loop_delta<.15,'Visible jump at the loop boundary'
            assert max_delta<1.0,'Animation changes too much of the frame at once'
        still=np.array(Image.open(target/'network-static.png').convert('RGB'))
        composed=np.concatenate([np.array(Image.open(target/f"{p['id']}.png").convert('RGB')) for p in CFG['panels']],axis=1)
        assert np.array_equal(still,composed),'Static panel seam'
        for project in CFG['projects']:
            route=project[variant]['route'];expected=CFG['core'][variant]['ports'][project[variant]['core_port']]
            assert route[0]==expected and route[-1]==project[variant]['input'],'A cable misses its configured port'
            for a,b in zip(route,route[1:]):
                dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1]);assert dx==0 or dy==0 or math.isclose(dx,dy),'Cable has an arbitrary-angle bend'
        size=sum((target/f"{p['id']}.gif").stat().st_size for p in CFG['panels'])
        assert size<CFG['animation']['tile_budget_bytes'],'Animation exceeds the payload budget'
        report['variants'][variant]={'sampled_frames':frames,'decoded_panels_match_master':True,'boundary_pixel_change':max_edge_change,'loop_mean_delta':loop_delta,'max_adjacent_frame_mean_delta':max_delta,'tile_bytes':size,'exact_connector_endpoints':True}
    browser_path=ROOT/'assets/previews/blueprint/browser-report.json'
    if browser_path.exists():
        browser=json.loads(browser_path.read_text(encoding='utf-8'))
        assert browser['status']=='passed','Browser checks failed'
        assert browser['readme_sha256']==hashlib.sha256(readme.encode()).hexdigest(),'Browser checks refer to a different README'
        for relative,digest in browser['assets_sha256'].items():
            assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,'Assets changed since browser checks; regenerate the preview'
        report['browser']='Seven widths, actual GitHub sanitization and CSS, pointer/keyboard links, reduced motion, and light/dark: passed'
    if args.check_links:
        urls=markup.links|set(re.findall(r'\]\((https?://[^)]+)\)',readme))
        urls=sorted({urldefrag(unescape(url))[0] for url in urls if url.startswith('https://github.com/')})
        with ThreadPoolExecutor(max_workers=4) as pool:report['github_links']=list(pool.map(check_url,urls))
    destination=ROOT/'assets/previews/blueprint';destination.mkdir(parents=True,exist_ok=True)
    (destination/'validation-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
