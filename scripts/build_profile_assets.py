"""Build animated section titles and project artwork."""
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
from functools import lru_cache
import base64
from profile_common import ROOT,CONFIG,MEDIA,write_if_changed

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
def build_titles(only=None):
    p=CONFIG['theme'];scale=3
    titles=[('projects','Projects'),('github-activity','GitHub Activity')]
    for slug,title in titles:
        if only is not None and slug not in only:continue
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
            # Preserve the title pixels; animate only its divider.
            left=start/scale;right=end/scale;center=h/2
            payload=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
                     f'<title>{title}</title>'
                     f'<defs><clipPath id="rule"><rect x="{left:.2f}" y="{center-3}" width="{right-left:.2f}" height="6"/></clipPath>'
                     f'<linearGradient id="sweep"><stop stop-color="{p["blue"]}" stop-opacity="0"/>'
                     f'<stop offset=".6" stop-color="{p["silver"]}"/><stop offset="1" stop-color="{p["blue"]}" stop-opacity="0"/></linearGradient></defs>'
                     f'<image href="{uri(image)}" width="{w}" height="{h}"/>'
                     f'<g clip-path="url(#rule)"><rect x="{left-90:.2f}" y="{center-1}" width="90" height="2" fill="url(#sweep)">'
                     f'<animate attributeName="x" from="{left-90:.2f}" to="{right:.2f}" dur="6s" repeatCount="indefinite"/></rect></g>'
                     f'<path d="M{w-32} {h-1}H{w-1}" stroke="{p["silver"]}" stroke-opacity="0">'
                     '<animate attributeName="stroke-opacity" values="0;.35;0" dur="6s" repeatCount="indefinite"/></path></svg>')
            write_if_changed(MEDIA/f'title-{slug}-animated{"-mobile" if mobile else ""}.svg',payload)


def main():
    from build_carousel import build_carousel
    MEDIA.mkdir(parents=True,exist_ok=True)
    build_titles()
    build_carousel()
    from build_project_table import build_project_table
    build_project_table()

if __name__=='__main__':main()
