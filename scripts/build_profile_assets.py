"""Build the preserved brand mark and distinct project carousel cards."""
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


def build_brand_logo():
    scale=3;width,height=56,78
    image=Image.new('RGBA',(width*scale,height*scale))
    ImageDraw.Draw(image).rounded_rectangle((0,0,width*scale-1,height*scale-1),8*scale,fill='#1a202a')
    logo=ImageOps.contain(prepare_logo(),((width-10)*scale,(height-12)*scale),LANCZOS)
    image.alpha_composite(logo,((image.width-logo.width)//2,(image.height-logo.height)//2))
    image.save(MEDIA/'personal-mark.png',optimize=True)


def main():
    from build_carousel import build_carousel
    MEDIA.mkdir(parents=True,exist_ok=True);(OUT/'build').mkdir(exist_ok=True)
    build_brand_logo()
    build_carousel()

if __name__=='__main__':main()
