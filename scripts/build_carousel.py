"""Compose original project marks and animate a single lossless horizontal carousel."""
from PIL import Image,ImageDraw,ImageOps
from html import escape
import hashlib
import json
from profile_common import ROOT,CONFIG,OUT,MEDIA

def draw_slide(project,index,mobile):
    # Import authored typography without importing this module back from the builder.
    from build_profile_assets import label,LANCZOS
    spec=CONFIG['carousel'];w=spec['mobile_width'] if mobile else spec['width'];h=spec['mobile_height'] if mobile else spec['height']
    footer=48;body=h-footer;vigil=project['id']=='vigil'
    surface='#edf4fd' if vigil else '#152026';ink='#15243d' if vigil else '#f0e9df';muted='#526b8c' if vigil else '#b4c0bb'
    image=Image.new('RGB',(w,h),surface);d=ImageDraw.Draw(image)
    if vigil:
        for gx in range(w//2,w,40):d.line((gx,0,gx,body),fill='#e2ebf7')
        for gy in range(12,body,40):d.line((w//2,gy,w,gy),fill='#e2ebf7')
    else:
        d.rectangle((0,0,5,body),fill='#9e5c51')
    x=26 if mobile else 44
    label(d,(x,22 if mobile else 30),f'{index+1:02d} / {len(CONFIG["projects"]):02d}',14,muted,mono=True)
    if vigil:
        label(d,(x,60 if mobile else 108),'Vigil',48 if mobile else 68,ink,600)
        label(d,(x,117 if mobile else 196),'Incident management platform',20 if mobile else 24,muted,450)
    else:
        label(d,(x,60 if mobile else 108),project['name'],44 if mobile else 64,ink,600)
        label(d,(x,117 if mobile else 196),'AI-assisted development case study',19 if mobile else 23,muted,450)
    if not mobile:d.line((x,263,x+50,263),fill=project['accent'],width=2)
    source=Image.open(ROOT/project['logo']).convert('RGBA')
    # The supplied PNG has alpha 1–3 noise far outside the visible mark.
    # Crop that padding without changing any retained color or alpha pixels.
    visible=source.getchannel('A').point(lambda a:255 if a>=4 else 0).getbbox()
    bounds=(max(0,visible[0]-8),max(0,visible[1]-8),min(source.width,visible[2]+8),min(source.height,visible[3]+8))
    cropped=source.crop(bounds)
    limit=(244,224) if mobile else (310,272)
    logo=ImageOps.contain(cropped,limit,LANCZOS)
    cx,cy=(w//2,body-133) if mobile else (w-224,body//2+3)
    xy=(cx-logo.width//2,cy-logo.height//2)
    # Keep the original logo pixels on an unobstructed part of each unique surface.
    if vigil:d.rectangle((xy[0],xy[1],xy[0]+logo.width,xy[1]+logo.height),fill=surface)
    image.paste(logo,xy,logo)
    d=ImageDraw.Draw(image)
    d.rectangle((0,body,w,h),fill='#0f151c');d.line((0,body,w,body),fill='#27313d')
    label(d,(x,body+14),'Explore projects',18 if mobile else 19,'#bac6d4',450)
    ax=x+(168 if mobile else 178);ay=body+23
    d.line((ax,ay-6,ax,ay+7),fill='#a8b8cc',width=2);d.line((ax-5,ay+2,ax,ay+7,ax+5,ay+2),fill='#a8b8cc',width=2)
    d.rounded_rectangle((1,1,w-2,h-2),12,outline='#2b3542',width=2)
    return image,{'file':project['logo'],'source_sha256':hashlib.sha256((ROOT/project['logo']).read_bytes()).hexdigest(),'crop':list(bounds),'position':list(xy),'size':list(logo.size),'background':surface,'operations':['crop near-transparent outer padding','proportional resize','alpha composite']}

def build_carousel():
    from build_profile_assets import uri
    spec=CONFIG['carousel'];report={}
    hold=spec['hold_ms']/1000;transition=spec['transition_ms']/1000;count=len(CONFIG['projects'])
    duration=count*(hold+transition)
    for mobile in (False,True):
        name='projects-carousel'+('-mobile' if mobile else '')
        slides=[];logos=[]
        for i,project in enumerate(CONFIG['projects']):
            slide,record=draw_slide(project,i,mobile);slides.append(slide);logos.append(record)
            slide.save(OUT/'build'/f'carousel-{project["id"]}{"-mobile" if mobile else ""}.png',optimize=True)
        w,h=slides[0].size;footer=48;body=h-footer
        title='Projects carousel — '+', '.join(p['name'] for p in CONFIG['projects'])
        svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title><desc>One project at a time. Each project is held for three seconds. Open the carousel to reach the projects list.</desc><defs><clipPath id="frame"><rect width="{w}" height="{h}" rx="12"/></clipPath></defs><g clip-path="url(#frame)"><g id="track">']
        values=['0 0'];times=[0];splines=[]
        for i in range(count):
            values.extend([f'{-i*w} 0',f'{-(i+1)*w} 0']);times.extend([(i*(hold+transition)+hold)/duration,(i+1)*(hold+transition)/duration]);splines.extend(['0 0 1 1','0.22 1 0.36 1'])
        for i,slide in enumerate([*slides,slides[0]]):svg.append(f'<image href="{uri(slide.crop((0,0,w,body)))}" x="{i*w}" width="{w}" height="{body}"/>')
        svg.append(f'<animateTransform attributeName="transform" type="translate" values="{";".join(values)}" keyTimes="{";".join(f"{t:.8f}" for t in times)}" keySplines="{";".join(splines)}" calcMode="spline" dur="{duration}s" repeatCount="indefinite"/></g></g>')
        svg.append(f'<image href="{uri(slides[0].crop((0,body,w,h)))}" y="{body}" width="{w}" height="{footer}"/>')
        dot_y=body+25;dot_start=w-93;dot_gap=36
        switches=[0]+[(i*(hold+transition)+hold+transition/2)/duration for i in range(count)]+[1]
        for i in range(count):
            x=dot_start+i*dot_gap
            states=[1 if i==0 else 0]+[1 if (j+1)%count==i else 0 for j in range(count)]+[1 if i==0 else 0]
            svg.append(f'<rect x="{x}" y="{dot_y}" width="22" height="3" rx="1.5" fill="#46566a"/><rect x="{x}" y="{dot_y}" width="22" height="3" rx="1.5" fill="#edf2f7" opacity="{states[0]}"><animate attributeName="opacity" values="{";".join(map(str,states))}" keyTimes="{";".join(f"{t:.8f}" for t in switches)}" calcMode="discrete" dur="{duration}s" repeatCount="indefinite"/></rect>')
        svg.append(f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="12" fill="none" stroke="#2b3542" stroke-width="2"/></svg>')
        target=MEDIA/f'{name}.svg';target.write_text(''.join(svg),encoding='utf-8',newline='\n')
        static=slides[0].copy();d=ImageDraw.Draw(static)
        for i in range(count):d.rounded_rectangle((dot_start+i*dot_gap,dot_y,dot_start+i*dot_gap+22,dot_y+3),1,fill='#edf2f7' if i==0 else '#46566a')
        static.save(MEDIA/f'{name}.png',optimize=True)
        report[name]={'format':'svg','motion':'slide','width':w,'height':h,'bytes':target.stat().st_size,'duration_ms':round(duration*1000),'hold_ms':spec['hold_ms'],'transition_ms':spec['transition_ms'],'projects':[p['id'] for p in CONFIG['projects']],'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'logos':logos}
        # Reduced motion keeps automatic content changes, with no moving transition.
        import xml.etree.ElementTree as ET
        doc=ET.fromstring(''.join(svg));ns={'s':'http://www.w3.org/2000/svg'}
        anim=doc.find('.//s:animateTransform',ns)
        anim.attrib.update({'values':';'.join(f'{-i*w} 0' for i in range(count+1)),'keyTimes':';'.join(str(i/count) for i in range(count+1)),'calcMode':'discrete','dur':f'{count*hold}s'})
        anim.attrib.pop('keySplines',None)
        for i,a in enumerate(doc.findall('.//s:animate',ns)):
            a.attrib.update({'dur':f'{count*hold}s','keyTimes':';'.join(str(j/count) for j in range(count+1)),'values':';'.join(str(int(j%count==i)) for j in range(count+1))})
        ET.register_namespace('','http://www.w3.org/2000/svg')
        reduced=MEDIA/f'{name}-reduced.svg';reduced.write_text(ET.tostring(doc,encoding='unicode'),encoding='utf-8',newline='\n')
        report[name+'-reduced']={**report[name],'motion':'cut','bytes':reduced.stat().st_size,'duration_ms':round(count*hold*1000),'transition_ms':0,'sha256':hashlib.sha256(reduced.read_bytes()).hexdigest()}
    assert sum(p['bytes'] for p in report.values())<spec['total_budget_bytes'],'Carousel exceeds its media budget'
    (MEDIA/'media-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({name:{key:value for key,value in item.items() if key!='logos'} for name,item in report.items()},indent=2))
