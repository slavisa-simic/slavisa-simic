"""Create the typing identity and one carousel from the official project marks."""
from PIL import Image,ImageDraw,ImageFont,ImageOps
from io import BytesIO
from functools import lru_cache
from html import escape
import base64
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


def main():
    from build_carousel import build_carousel
    MEDIA.mkdir(parents=True,exist_ok=True);(OUT/'build').mkdir(exist_ok=True)
    for dark in (False,True):
        for mobile in (False,True):typing_identity(dark,mobile)
    build_carousel()

if __name__=='__main__':main()
