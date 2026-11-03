"""Create two correctly linked project slideshows and a locally hosted typing identity."""
from PIL import Image,ImageDraw,ImageFont,ImageOps
from io import BytesIO
from functools import lru_cache
from html import escape
import base64
import hashlib
import json
import math
import numpy as np
from profile_common import ROOT,CONFIG,OUT,MEDIA,SOURCE

LANCZOS=Image.Resampling.LANCZOS
@lru_cache(maxsize=64)
def font(size,weight=500,mono=False):
    path=ROOT/'assets/source/fonts'/('IBMPlexMono-Regular.ttf' if mono else 'Inter.ttf')
    face=ImageFont.truetype(str(path),size)
    if not mono:
        axes=face.get_variation_axes()
        face.set_variation_by_axes([weight if b'Weight' in a['name'] else a['default'] for a in axes])
    return face
def rgb(value):return tuple(bytes.fromhex(value.lstrip('#')))
def label(draw,position,value,size,color,weight=500,anchor='lt',mono=False):
    draw.text(position,value,font=font(size,weight,mono),fill=color,anchor=anchor)
def uri(image):
    data=BytesIO();image.save(data,format='PNG',optimize=True)
    return 'data:image/png;base64,'+base64.b64encode(data.getvalue()).decode()
def prepare_logo():
    source=np.array(Image.open(ROOT/'assets/source/personal-logo.png').convert('RGBA'))
    light=source[:,:,:3].max(axis=2).astype(float)
    source[:,:,3]=np.clip((light-5)/25*255,0,255).astype('uint8')
    image=Image.fromarray(source);return image.crop(image.getchannel('A').getbbox())

def typing_identity(dark,mobile):
    width,height=(360,126) if mobile else (720,112)
    tint='#edf2f7' if dark else '#17233a';secondary='#acb9cb' if dark else '#48596e'
    scale=3;static=Image.new('RGBA',(width*scale,height*scale))
    sd=ImageDraw.Draw(static)
    tile=(0,6,38,53) if mobile else (0,9,47,75)
    sd.rounded_rectangle(tuple(round(v*scale) for v in tile),radius=8*scale,fill='#192538')
    logo=ImageOps.contain(prepare_logo(),((tile[2]-tile[0]-10)*scale,(tile[3]-tile[1]-12)*scale),LANCZOS)
    logo_xy=((tile[0]+tile[2])*scale//2-logo.width//2,(tile[1]+tile[3])*scale//2-logo.height//2)
    static.alpha_composite(logo,logo_xy)
    logo_layer=Image.new('RGBA',static.size);logo_layer.alpha_composite(logo,logo_xy)
    body=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>{escape(CONFIG["name"])} — {escape(" / ".join(CONFIG["roles"]))}</title><desc>Name and role type once, then remain visible.</desc><rect x="{tile[0]}" y="{tile[1]}" width="{tile[2]-tile[0]}" height="{tile[3]-tile[1]}" rx="8" fill="#192538"/><image href="{uri(logo_layer.resize((width,height),LANCZOS))}" width="{width}" height="{height}"/>']
    lines=[(CONFIG['name'],49 if mobile else 65,4 if mobile else 7,30 if mobile else 44,tint,.1,.075)]
    if mobile:
        lines += [(CONFIG['roles'][0],49,51,17,secondary,1.5,.055),(CONFIG['roles'][1],49,77,17,secondary,2.55,.055)]
    else:lines += [(' / '.join(CONFIG['roles']),67,66,21,secondary,1.5,.05)]
    for index,(value,x,y,size,color,start,step) in enumerate(lines):
        face=font(size*scale,600 if index==0 else 450)
        tw=math.ceil(face.getlength(value))+6*scale;th=math.ceil(size*1.5)*scale
        image=Image.new('RGBA',(tw,th));d=ImageDraw.Draw(image);d.text((0,0),value,font=face,fill=color,anchor='lt')
        static.alpha_composite(image,(x*scale,y*scale))
        logical_w=tw/scale;logical_h=th/scale;duration=4.2
        times=[0,start]+[start+step*(i+1) for i in range(len(value))]+[duration]
        widths=[0,0]+[min(logical_w,face.getlength(value[:i+1])/scale+2) for i in range(len(value))]+[logical_w]
        values=';'.join(f'{v:.3f}' for v in widths);keys=';'.join(f'{t/duration:.6f}' for t in times)
        body.append(f'<defs><clipPath id="line-{index}"><rect width="{logical_w}" height="{logical_h}"><animate attributeName="width" values="{values}" keyTimes="{keys}" calcMode="discrete" dur="{duration}s" fill="freeze"/></rect></clipPath></defs><g transform="translate({x} {y})"><image href="{uri(image)}" width="{logical_w}" height="{logical_h}" clip-path="url(#line-{index})"/></g>')
        cursor_times=times[:-1]+[times[-2]+.06,duration]
        cursor_values=widths[:-1]+[widths[-2],widths[-2]]
        end=times[-2]+.1
        body.append(f'<g transform="translate({x} {y})"><rect x="{widths[-2]}" y="0" width="2" height="{size+2}" fill="{color}" opacity="0"><animate attributeName="x" values="{";".join(f"{v:.3f}" for v in cursor_values)}" keyTimes="{";".join(f"{t/duration:.6f}" for t in cursor_times)}" calcMode="discrete" dur="{duration}s" fill="freeze"/><animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;{start/duration:.6f};{(end-.01)/duration:.6f};{end/duration:.6f};1" calcMode="discrete" dur="{duration}s" fill="freeze"/></rect></g>')
    body.append('</svg>')
    name=f'identity{"-mobile" if mobile else ""}-{"dark" if dark else "light"}'
    (MEDIA/f'{name}.svg').write_text(''.join(body),encoding='utf-8')
    static.resize((width*2,height*2),LANCZOS).save(MEDIA/f'{name}.png',optimize=True)

def rounded(image,radius):
    mask=Image.new('L',image.size);ImageDraw.Draw(mask).rounded_rectangle((0,0,image.width-1,image.height-1),radius,fill=255)
    result=image.convert('RGBA');result.putalpha(mask);return result

def slide(project,index):
    width,height=CONFIG['preview']['width'],CONFIG['preview']['height']
    surface=rgb(project['surface']);ink=rgb(project['ink']);accent=rgb(project['accent'])
    image=Image.new('RGB',(width,height),surface);d=ImageDraw.Draw(image)
    right=(420,24,width-24,height-24)
    if index==0:
        hero=Image.open(SOURCE/f"{project['id']}-hero.png").convert('RGB')
        crop=hero.crop((850,0,hero.width,hero.height)) if project['id']=='vigil' else hero.crop((854,0,1280,350))
        art=ImageOps.fit(crop,(width-360,height),LANCZOS)
        alpha=Image.new('L',art.size,255);a=np.array(alpha)
        a[:,:120]=np.linspace(0,255,120,dtype='uint8')[None,:]
        image.paste(art,(360,0),Image.fromarray(a))
    elif index==1:
        capture=Image.open(SOURCE/f"{project['id']}-screen.png").convert('RGB')
        fitted=ImageOps.contain(capture,(right[2]-right[0]-12,right[3]-right[1]-72),LANCZOS)
        x=right[0]+(right[2]-right[0]-fitted.width)//2;y=(height-fitted.height)//2
        d.rounded_rectangle((right[0],y-18,right[2],y+fitted.height+18),12,fill='#ffffff' if project['id']=='vigil' else '#0b1317',outline='#c7d6ec' if project['id']=='vigil' else '#3d4c4f',width=2)
        image.paste(fitted,(x,y))
    else:
        for i,value in enumerate(project['flow']):
            x0,x1=right[0]+8,right[2]-8;y=59+i*135
            d.rounded_rectangle((x0,y,x1,y+85),12,fill='#e7effb' if project['id']=='vigil' else '#202d33',outline=accent,width=2)
            label(d,((x0+x1)/2,y+42),value,27,ink,500,'mm')
            if i<2:
                x=(x0+x1)//2;d.line((x,y+86,x,y+119),fill=accent,width=2);d.line([(x-6,y+111),(x,y+119),(x+6,y+111)],fill=accent,width=2)
    # A persistent project identity keeps every slide's destination unambiguous.
    d=ImageDraw.Draw(image)
    label(d,(40,38),'SELECTED PROJECT',19,ink,450,mono=True)
    label(d,(40,166),project['name'],91 if project['id']=='vigil' else 67,ink,650)
    d.line((42,286,118,286),fill=accent,width=3)
    label(d,(42,320),project['slides'][index],25,ink,450)
    label(d,(42,433),'Open README',22,ink,500)
    d.line((221,445,237,429),fill=ink,width=2);d.line((225,429,237,429,237,441),fill=ink,width=2)
    for i in range(3):d.rounded_rectangle((width-105+i*25,height-28,width-91+i*25,height-24),2,fill=accent if i==index else ('#b6c6df' if project['id']=='vigil' else '#52616a'))
    d.rounded_rectangle((1,1,width-2,height-2),16,outline='#bacbe4' if project['id']=='vigil' else '#46575e',width=2)
    return image

def mobile_slide(project,index):
    """Use a larger identity and cropped artwork in narrow two-column layouts."""
    width,height=360,320
    image=Image.new('RGB',(width,height),project['surface']);d=ImageDraw.Draw(image)
    ink=rgb(project['ink']);accent=rgb(project['accent'])
    label(d,(20,23),project['name'],50,ink,650)
    if index==0:
        hero=Image.open(SOURCE/f"{project['id']}-hero.png").convert('RGB')
        hero=hero.crop((850,0,hero.width,hero.height)) if project['id']=='vigil' else hero.crop((854,0,1280,350))
        art=ImageOps.fit(hero,(328,204),LANCZOS)
    else:
        source=Image.open(SOURCE/f"{project['id']}-screen.png").convert('RGB')
        art=ImageOps.contain(source,(328,204),LANCZOS)
    image.paste(art,((width-art.width)//2,99+(204-art.height)//2))
    d=ImageDraw.Draw(image)
    d.line((20,85,73,85),fill=accent,width=2)
    for i in range(2):d.rounded_rectangle((316+i*14,83,325+i*14,86),1,fill=accent if i==index else ('#b6c6df' if project['id']=='vigil' else '#52616a'))
    d.rounded_rectangle((1,1,width-2,height-2),10,outline='#bacbe4' if project['id']=='vigil' else '#46575e',width=2)
    return image

def animate(project,slides,suffix=''):
    spec=CONFIG['preview'];frames=[];durations=[]
    for index,current in enumerate(slides):
        frames.append(current);durations.append(spec['hold_ms'])
        following=slides[(index+1)%len(slides)]
        for step in range(1,spec['transition_frames']+1):
            t=step/(spec['transition_frames']+1);t=t*t*(3-2*t)
            frames.append(Image.blend(current,following,t));durations.append(spec['transition_ms']//spec['transition_frames'])
    sample=Image.new('RGB',(slides[0].width*len(slides),slides[0].height))
    for i,frame in enumerate(slides):sample.paste(frame,(i*frame.width,0))
    palette=sample.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
    encoded=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    target=MEDIA/f"{project['id']}{suffix}.gif"
    encoded[0].save(target,save_all=True,append_images=encoded[1:],loop=0,duration=durations,disposal=1,optimize=True)
    slides[0].save(MEDIA/f"{project['id']}{suffix}.png",optimize=True)
    return {'bytes':target.stat().st_size,'duration_ms':sum(durations),'samples':len(frames),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}

def main():
    MEDIA.mkdir(parents=True,exist_ok=True);(OUT/'build').mkdir(exist_ok=True)
    for dark in (False,True):
        for mobile in (False,True):typing_identity(dark,mobile)
    report={}
    for project in CONFIG['projects']:
        slides=[slide(project,i) for i in range(3)]
        for i,frame in enumerate(slides):frame.save(OUT/'build'/f"{project['id']}-{i}.png")
        report[project['id']]=animate(project,slides)
        report[project['id']+'-mobile']=animate(project,[mobile_slide(project,i) for i in range(2)],'-mobile')
    assert sum(p['bytes'] for p in report.values())<CONFIG['preview']['total_budget_bytes'],'Project previews exceed the budget'
    (MEDIA/'media-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
