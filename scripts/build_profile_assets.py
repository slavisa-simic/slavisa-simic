"""Build blueprint title strips and distinct project carousel cards."""
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
from functools import lru_cache
import base64
from profile_common import ROOT,CONFIG,OUT,MEDIA

LANCZOS=Image.Resampling.LANCZOS
@lru_cache(maxsize=64)
def font(size,weight=500,mono=False):
    path=ROOT/'assets/source/fonts'/('IBMPlexMono-Regular.ttf' if mono else 'Inter.ttf')
    face=ImageFont.truetype(str(path),size)
    if not mono:
        axes=face.get_variation_axes()
        face.set_variation_by_axes([weight if b'Weight' in a['name'] else a['default'] for a in axes])
    return face
def label(draw,position,value,size,color,weight=500,anchor='lt',mono=False):
    draw.text(position,value,font=font(size,weight,mono),fill=color,anchor=anchor)
def uri(image):
    data=BytesIO();image.save(data,format='PNG',optimize=True)
    return 'data:image/png;base64,'+base64.b64encode(data.getvalue()).decode()
def build_titles():
    p=CONFIG['theme'];scale=3
    titles=[('projects','Projects'),('projects-list','Projects list'),('tech-stack','Tech stack')]
    for slug,title in titles:
        for mobile in (False,True):
            w,h=(360,46) if mobile else (860,50)
            image=Image.new('RGB',(w*scale,h*scale),p['surface']);d=ImageDraw.Draw(image)
            # One typeface, hairline geometry, and the exact reference palette.
            d.rectangle((0,0,w*scale-1,h*scale-1),outline=p['line'],width=scale)
            d.line((0,0,32*scale,0),fill=p['blue'],width=2*scale)
            d.line(((w-32)*scale,(h-1)*scale,(w-1)*scale,(h-1)*scale),fill=p['red'],width=scale)
            label(d,(18*scale,h*scale//2),title,(21 if mobile else 23)*scale,p['text'],550,anchor='lm')
            tw=d.textlength(title,font=font((21 if mobile else 23)*scale,550))
            start=18*scale+tw+24*scale;end=(w-24)*scale
            d.line((start,h*scale//2,end,h*scale//2),fill=p['line'],width=scale)
            d.rectangle((end-3*scale,h*scale//2-2*scale,end+scale,h*scale//2+2*scale),fill=p['silver'])
            image.save(MEDIA/f'title-{slug}{"-mobile" if mobile else ""}.png',optimize=True)
    for slug,title,w in [('ai-tools','AI Development Tools',222),('project-notes','Project notes',140),('recent-changes','Recent changes',158)]:
        h=30;image=Image.new('RGB',(w*scale,h*scale),p['surface']);d=ImageDraw.Draw(image)
        d.rectangle((0,0,w*scale-1,h*scale-1),outline=p['line'],width=scale)
        d.line((0,0,16*scale,0),fill=p['blue'],width=scale)
        d.line(((w-16)*scale,(h-1)*scale,w*scale,(h-1)*scale),fill=p['red'],width=scale)
        label(d,(10*scale,h*scale//2),title,16*scale,p['text'],500,anchor='lm')
        image.save(MEDIA/f'title-{slug}.png',optimize=True)


def main():
    from build_carousel import build_carousel
    MEDIA.mkdir(parents=True,exist_ok=True);(OUT/'build').mkdir(exist_ok=True)
    build_titles()
    build_carousel()

if __name__=='__main__':main()
