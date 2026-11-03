"""Validate the native README, supplied marks, and lossless carousel images."""
from html.parser import HTMLParser
from hashlib import sha256
import json
import base64
from io import BytesIO
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
    assert markup.images==3,'Expected identity, one carousel, and activity'
    for relative in markup.assets:
        assert relative.startswith('assets/profile/generated/'),'Images must be stored in this repository'
        assert (ROOT/relative).is_file(),f'Missing image: {relative}'
    for project in CONFIG['projects']:
        assert project['readme'] in markup.links,'Missing project README destination'
        assert project['readme'].endswith('/blob/main/README.md'),'Project target must start at the README'
        assert sha256((ROOT/project['logo']).read_bytes()).hexdigest()==project['logo_sha256'],'Official logo source has changed'
    assert CONFIG['carousel']['target'] in markup.links,'Carousel must open the project list'
    assert '### Projects list' in readme,'Missing project list target'
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
    report={'status':'passed','assets':len(markup.assets),'activity_commits':stats['total_commits'],'carousel_variants':{}}
    manifest=json.loads((MEDIA/'media-manifest.json').read_text())
    for name,expected in manifest.items():
        svg=ET.parse(MEDIA/f'{name}.svg');ns={'s':'http://www.w3.org/2000/svg'}
        encoded=svg.findall('.//s:image',ns)
        holds=[Image.open(BytesIO(base64.b64decode(e.attrib['href'].split(',',1)[1]))).convert('RGB') for e in encoded[:len(CONFIG['projects'])]]
        clone=Image.open(BytesIO(base64.b64decode(encoded[len(holds)].attrib['href'].split(',',1)[1]))).convert('RGB')
        assert np.array_equal(np.asarray(clone),np.asarray(holds[0])),'Loop clone differs from the first project'
        motion=svg.find('.//s:animateTransform',ns)
        assert motion is not None and motion.attrib['repeatCount']=='indefinite'
        assert motion.attrib['type']=='translate' and motion.attrib['calcMode']=='spline'
        assert round(float(motion.attrib['dur'].removesuffix('s'))*1000)==expected['duration_ms']
        assert sha256((MEDIA/f'{name}.svg').read_bytes()).hexdigest()==expected['sha256']
        fallback=Image.open(MEDIA/f'{name}.png').convert('RGB')
        assert fallback.size==(expected['width'],expected['height'])
        assert np.array_equal(np.asarray(fallback)[:holds[0].height,8:-8],np.asarray(holds[0])[:,8:-8]),'Static fallback changes the first slide'
        for slide,logo in zip(holds,expected['logos']):
            source=Image.open(ROOT/logo['file']).convert('RGBA').crop(logo['crop']).resize(logo['size'],Image.Resampling.LANCZOS)
            composited=Image.new('RGB',source.size,slide.getpixel((8,100)));composited.paste(source,(0,0),source)
            x,y=logo['position'];actual=slide.crop((x,y,x+source.width,y+source.height))
            assert np.array_equal(np.asarray(actual),np.asarray(composited)),f'Logo colors or details have been modified: {logo["file"]}'
        report['carousel_variants'][name]={'bytes':expected['bytes'],'duration_ms':expected['duration_ms'],'projects':expected['projects'],'logo_pixels':'exact proportional source composites'}
    assert sum(v['bytes'] for v in manifest.values())<CONFIG['carousel']['total_budget_bytes']
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
