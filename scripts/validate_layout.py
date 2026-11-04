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
from tech_stack import STACK,description

class Markup(HTMLParser):
    def __init__(self):super().__init__();self.assets=set();self.links=[];self.images=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        assert tag not in ('script','style','iframe','canvas','map','svg'),f'Unsupported tag: {tag}'
        assert not any(k=='style' or k.startswith('on') for k in attrs),'Unsupported README scripting or styling'
        for key in ('src','srcset','href'):
            if key in attrs and attrs[key].startswith('assets/'):self.assets.add(attrs[key])
        if tag=='a' and 'href' in attrs:self.links.append(attrs['href'])
        if tag=='img':
            self.images+=1
            assert attrs.get('alt') or attrs.get('src','').endswith('header-spacer.svg'),'Missing image description'

def main():
    readme=(ROOT/'README.md').read_text(encoding='utf-8');markup=Markup();markup.feed(readme)
    assert markup.images==6+sum(3+len(p['showcase']['stack']) for p in CONFIG['projects']),'Unexpected profile image count'
    for relative in markup.assets:
        assert relative.startswith(('assets/profile/generated/','assets/profile/badges/')),'Images must be stored in this repository'
        assert (ROOT/relative).is_file(),f'Missing image: {relative}'
    for project in CONFIG['projects']:
        assert 'https://github.com/'+project['repository'] in markup.links,'Missing project repository destination'
        assert f'<h3>{project["name"]}</h3>' in readme and project['showcase']['description'] in readme,'Project copy must be native text'
        assert sha256((ROOT/project['logo']).read_bytes()).hexdigest()==project['logo_sha256'],'Official logo source has changed'
    assert CONFIG['carousel']['target'] in markup.links,'Carousel must open the project list'
    assert '<a name="projects-list"></a>' in readme,'Missing stable project list target'
    assert readme.count('<h2>Projects</h2>')==1 and 'All projects' not in readme,'Use one native Projects section'
    assert '<details>' not in readme and 'title-projects-list' not in readme and 'badge.svg' not in readme,'Retired footer is still visible'
    assert readme.count(CONFIG['intro'])<=1,'Repeated introduction'
    assert '{{' not in readme,'Unresolved template field'
    assert f'{CONFIG["name"]} — Software Engineer.' in readme,'Identity needs an accessible text equivalent'
    assert '~/' not in readme and 'whoami' not in readme,'Terminal presentation is retired'
    assert 'identity-dark.svg' not in readme and 'identity-dark.png' not in readme
    assert 'activity-dark.svg' not in readme,'Statistics must be native text, not an image'
    assert 'title-tech-stack' not in readme and 'title-ai-tools' not in readme,'Standalone stack must be removed'
    assert 'Unity' not in description() and 'Python' in description()
    assert 'Codex (AI development tool)' in description()
    assert 'Software Engineer' in readme and 'Backend Developer' not in readme
    assert CONFIG['linkedin'] in markup.links
    assert f'https://github.com/{CONFIG["owner"]}?tab=repositories' in markup.links
    for name,record in json.loads((OUT/'icons/provenance.json').read_text()).items():
        assert sha256((OUT/'icons'/name).read_bytes()).hexdigest()==record['sha256'],'Icon cache changed'
    for name,record in json.loads((MEDIA/'tech-manifest.json').read_text()).items():
        payload=(MEDIA/f'{name}.svg').read_bytes();assert sha256(payload).hexdigest()==record['sha256']
        document=ET.fromstring(payload);motion=document.find('.//{http://www.w3.org/2000/svg}animateTransform')
        if record['static']: assert motion is None
        else:
            assert motion.attrib['from']==f'-{record["period"]} 0' and motion.attrib['to']=='0 0'
            assert motion.attrib['calcMode']=='linear' and motion.attrib['repeatCount']=='indefinite'
        assert record['bytes']<100_000,'Tech asset exceeds budget'
    for name,record in json.loads((SOURCE/'provenance.json').read_text()).items():
        assert sha256((SOURCE/name).read_bytes()).hexdigest()==record['sha256'],f'Source changed: {name}'
    for name,record in json.loads((SOURCE/'preview-provenance.json').read_text()).items():
        assert sha256((SOURCE/name).read_bytes()).hexdigest()==record['sha256'],f'Project preview changed: {name}'
    stats=json.loads((OUT/'activity.json').read_text(encoding='utf-8'))
    assert sum(d['commits'] for d in stats['daily'])==stats['total_commits']
    assert len([d for d in stats['daily'] if d['commits']])==stats['active_days']
    assert len(stats['recent'])<=CONFIG['recent_limit']
    assert sum(p['commits_30d'] for p in stats['projects'])==stats['total_commits']
    for badge in json.loads((OUT/'badges/provenance.json').read_text()).values():assert badge['url'].startswith('https://img.shields.io/badge/')
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
        assert motion.attrib['type']=='translate' and motion.attrib['calcMode']==('discrete' if expected['motion']=='cut' else 'spline')
        assert round(float(motion.attrib['dur'].removesuffix('s'))*1000)==expected['duration_ms']
        assert sha256((MEDIA/f'{name}.svg').read_bytes()).hexdigest()==expected['sha256']
        fallback=Image.open(MEDIA/f'{name.removesuffix("-reduced")}.png').convert('RGB')
        assert fallback.size==(expected['width'],expected['height'])
        assert np.array_equal(np.asarray(fallback)[:holds[0].height,8:-8],np.asarray(holds[0])[:,8:-8]),'Static fallback changes the first slide'
        for slide,logo in zip(holds,expected['logos']):
            source=Image.open(ROOT/logo['file']).convert('RGBA').crop(logo['crop']).resize(logo['size'],Image.Resampling.LANCZOS)
            composited=Image.new('RGB',source.size,logo['background']);composited.paste(source,(0,0),source)
            x,y=logo['position'];actual=slide.crop((x,y,x+source.width,y+source.height))
            assert np.array_equal(np.asarray(actual),np.asarray(composited)),f'Logo colors or details have been modified: {logo["file"]}'
        report['carousel_variants'][name]={'bytes':expected['bytes'],'duration_ms':expected['duration_ms'],'projects':expected['projects'],'logo_pixels':'exact proportional source composites'}
    assert sum(v['bytes'] for v in manifest.values())<CONFIG['carousel']['total_budget_bytes']
    for svg in MEDIA.glob('*.svg'):
        document=ET.parse(svg)
        for element in document.iter():
            assert element.tag.split('}')[-1] not in ('script','foreignObject')
            for attribute,value in element.attrib.items():
                if attribute.endswith('href'):assert value.startswith(('#','data:image/svg+xml;base64,','data:image/png;base64,','data:image/jpeg;base64,','data:image/webp;base64,')),'SVG depends on an external resource'
    avatar=json.loads((OUT/'avatar.json').read_text())
    assert sha256(base64.b64decode(avatar['data_uri'].split(',')[1])).hexdigest()==avatar['sha256']
    assert avatar['source'].startswith('https://avatars.githubusercontent.com/')
    active=list(MEDIA.glob('profile-avatar-*.svg'));assert len(active)==1
    framed_uri='data:image/svg+xml;base64,'+base64.b64encode(active[0].read_bytes()).decode()
    for header in MEDIA.glob('profile-header*.svg'):
        contents=header.read_text(encoding='utf-8')
        assert framed_uri in contents,'Header must embed the exact original framed avatar'
        assert 'Software Engineer</text>' in contents and 'Backend Developer' not in contents
        assert 'Unity' not in contents and 'Python' in contents
        doc=ET.fromstring(contents);ns={'s':'http://www.w3.org/2000/svg'}
        photo=doc.find('s:image',ns);name=doc.find('.//s:text',ns);tech=doc.find('s:svg',ns)
        identity=doc.findall('s:g/s:text',ns)
        assert len(identity)==3 and len({t.attrib['x'] for t in identity})==1,'All identity lines must share the left edge'
        assert [int(t.attrib['font-weight']) for t in identity]==[700,500,400],'Identity needs a clear weight hierarchy'
        if '-mobile' in header.name:
            assert float(name.attrib['y'])>=float(photo.attrib['y'])+float(photo.attrib['height'])
            assert float(tech.attrib['y'])>float(name.attrib['y'])
        else:
            assert float(tech.attrib['x'])>=float(photo.attrib['x'])+float(photo.attrib['width'])
            assert name.attrib['x']==tech.attrib['x']
    frame=ET.parse(active[0]);photo=frame.find('.//s:image',{'s':'http://www.w3.org/2000/svg'})
    assert photo.attrib['href']==avatar['data_uri'],'Framed avatar pixels must match the downloaded original'
    for element in frame.findall('.//s:rect',{'s':'http://www.w3.org/2000/svg'}):assert 'rx' not in element.attrib
    destination=ROOT/'assets/previews/profile';destination.mkdir(parents=True,exist_ok=True)
    (destination/'validation-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
