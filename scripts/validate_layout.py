"""Validate the native README, original sources, and decoded slideshow frames."""
from html.parser import HTMLParser
from hashlib import sha256
import json
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from profile_common import ROOT,CONFIG,OUT,MEDIA,SOURCE

class Markup(HTMLParser):
    def __init__(self):super().__init__();self.assets=set();self.links=[];self.images=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        assert tag not in ('script','style','iframe','canvas','map','svg'),f'Unsupported tag: {tag}'
        assert not any(k=='style' or k.startswith('on') for k in attrs),'Unsupported README scripting or styling'
        for key in ('src','srcset'):
            if key in attrs:self.assets.add(attrs[key])
        if tag=='a':self.links.append(attrs['href'])
        if tag=='img':
            self.images+=1;assert attrs.get('alt'),'Missing image description'

def main():
    readme=(ROOT/'README.md').read_text(encoding='utf-8');markup=Markup();markup.feed(readme)
    assert markup.images==4,'Expected identity, two project previews, and activity'
    for relative in markup.assets:
        assert relative.startswith('assets/profile/generated/'),'Images must be stored in this repository'
        assert (ROOT/relative).is_file(),f'Missing image: {relative}'
    for project in CONFIG['projects']:
        assert project['readme'] in markup.links,'Missing project README destination'
        assert project['readme'].endswith('/blob/main/README.md'),'Project target must start at the README'
    assert readme.count(CONFIG['intro'])==1,'Repeated introduction'
    assert '{{' not in readme,'Unresolved template field'
    toolkit=readme.split('## Toolkit')[1].split('## Recent work')[0]
    assert 'Unity' not in toolkit and 'C#' not in toolkit,'Unsupported personal skill'
    assert '**AI Development Tools:** OpenAI Codex' in toolkit
    for name,record in json.loads((SOURCE/'provenance.json').read_text()).items():
        assert sha256((SOURCE/name).read_bytes()).hexdigest()==record['sha256'],f'Source changed: {name}'
    stats=json.loads((OUT/'activity.json').read_text(encoding='utf-8'))
    assert sum(d['commits'] for d in stats['daily'])==stats['total_commits']
    assert len([d for d in stats['daily'] if d['commits']])==stats['active_days']
    assert len(stats['recent'])<=CONFIG['recent_limit']
    report={'status':'passed','assets':len(markup.assets),'activity_commits':stats['total_commits'],'gif_variants':{}}
    manifest=json.loads((MEDIA/'media-manifest.json').read_text())
    for name,expected in manifest.items():
        gif=Image.open(MEDIA/f'{name}.gif');durations=[];holds=[]
        for index in range(gif.n_frames):
            gif.seek(index);durations.append(gif.info['duration'])
            if gif.info['duration']==CONFIG['preview']['hold_ms']:holds.append(gif.convert('RGB'))
        assert gif.n_frames==expected['samples']
        assert sum(durations)==expected['duration_ms']
        assert gif.info['loop']==0
        assert len(holds)==(2 if name.endswith('-mobile') else 3)
        assert all(d==40 or d==5000 for d in durations),'Unexpected playback timing'
        assert sha256((MEDIA/f'{name}.gif').read_bytes()).hexdigest()==expected['sha256']
        fallback=Image.open(MEDIA/f'{name}.png').convert('RGB')
        error=float(np.abs(np.asarray(fallback,dtype=float)-np.asarray(holds[0],dtype=float)).mean())
        assert error<5,'First frame differs from the complete static fallback'
        assert all(np.abs(np.asarray(a,dtype=float)-np.asarray(b,dtype=float)).mean()>1 for a,b in zip(holds,holds[1:])),'Slideshow frames do not change'
        report['gif_variants'][name]={'bytes':expected['bytes'],'decoded_frames':gif.n_frames,'duration_ms':sum(durations),'first_frame_mean_error':round(error,3)}
    assert sum(v['bytes'] for v in manifest.values())<CONFIG['preview']['total_budget_bytes']
    for svg in MEDIA.glob('*.svg'):
        document=ET.parse(svg)
        for element in document.iter():
            assert element.tag.split('}')[-1] not in ('script','foreignObject')
            for attribute,value in element.attrib.items():
                if attribute.endswith('href'):assert value.startswith('data:image/png;base64,'),'SVG depends on an external resource'
    destination=ROOT/'assets/previews/profile';destination.mkdir(parents=True,exist_ok=True)
    (destination/'validation-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
