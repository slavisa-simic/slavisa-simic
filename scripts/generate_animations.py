"""Render subtle motion over the approved static blueprint. All panels share one film."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/blueprint'
CFG=json.loads((ROOT/'config/network.json').read_text(encoding='utf-8'))
LANCZOS=Image.Resampling.LANCZOS

def color(value): return tuple(bytes.fromhex(value.lstrip('#')))
def smooth(t):
    t=max(0,min(1,t)); return t*t*(3-2*t)
def path_length(points): return sum(math.dist(a,b) for a,b in zip(points,points[1:]))
def point_at(points,distance):
    for a,b in zip(points,points[1:]):
        segment=math.dist(a,b)
        if distance<=segment:
            return tuple(x+(y-x)*max(0,distance)/segment for x,y in zip(a,b))
        distance-=segment
    return points[-1]

class Film:
    def __init__(self,variant):
        self.variant=variant
        self.layout=CFG['exports'][variant]
        self.width=1120
        self.height=round(self.layout['diagram_height']*self.width/self.layout['width'])
        self.sx=self.width/self.layout['width']; self.sy=self.height/self.layout['diagram_height']
        self.base=Image.open(OUT/'build'/f'{variant}-network-base.png').convert('RGB').resize((self.width,self.height),LANCZOS)
        self.cuts=[round(self.width*p['end']) for p in CFG['panels'][:-1]]
        box=CFG['core'][variant]['logo']
        x,y,w,h=box
        self.logo=ImageOps.contain(Image.open(OUT/'source/logo.png').convert('RGBA'),(round(w*self.sx),round(h*self.sy)),LANCZOS)
        self.logo_xy=(round((self.layout['padding']+x)*self.sx+(w*self.sx-self.logo.width)/2),round(y*self.sy+(h*self.sy-self.logo.height)/2))
        self.paths={p['id']:[self.xy(v) for v in p[variant]['route']] for p in CFG['projects']}

    def xy(self,point): return ((point[0]+self.layout['padding'])*self.sx,point[1]*self.sy)

    def frame(self,time,still=False):
        image=self.base.convert('RGBA')
        logo=self.logo.copy()
        animation=CFG['animation']
        dissolve,assemble=animation['dissolve'],animation['assemble']
        alpha=np.array(logo.getchannel('A'),dtype=np.float32)
        if not still:
            if dissolve[0]<=time<dissolve[1]:
                alpha*=1-.94*smooth((time-dissolve[0])/(dissolve[1]-dissolve[0]))
            elif assemble[0]<=time<assemble[1]:
                progress=smooth((time-assemble[0])/(assemble[1]-assemble[0]))
                yy,xx=np.mgrid[:logo.height,:logo.width]
                scan=yy/logo.height*.84+(1-xx/logo.width)*.16
                alpha*=.06+.94*np.clip((progress-scan)*32,0,1)
        logo.putalpha(Image.fromarray(alpha.astype('uint8')))
        image.alpha_composite(logo,self.logo_xy)
        overlay=Image.new('RGBA',image.size); d=ImageDraw.Draw(overlay)
        if not still and assemble[0]<=time<assemble[1]:
            progress=smooth((time-assemble[0])/(assemble[1]-assemble[0]))
            yy,xx=np.mgrid[:logo.height,:logo.width]
            scan=yy/logo.height*.84+(1-xx/logo.width)*.16
            trace=Image.new('RGBA',logo.size,(237,243,250))
            mask=np.array(self.logo.getchannel('A'),dtype=float)*np.clip(1-abs(scan-progress)/.03,0,1)
            trace.putalpha(Image.fromarray(mask.astype('uint8')))
            overlay.alpha_composite(trace,self.logo_xy)
        for project in CFG['projects']:
            tint=color(CFG['theme'][project['color']]); points=self.paths[project['id']]
            extent=path_length(points)
            if still:
                x,y=point_at(points,extent*.85)
                radius=1.8*self.sx
                d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(*tint,230))
                continue
            for start,end in animation['send']:
                if start<=time<=end:
                    fraction=(time-start)/(end-start)
                    tail=12*self.sx
                    head=fraction*(extent+tail)
                    for distance in np.arange(max(0,head-tail),min(extent,head),.8):
                        x,y=point_at(points,distance)
                        guard=min(smooth((abs(x-cut)-4)/animation['boundary_guard']) for cut in self.cuts)
                        gain=max(0,1-(head-distance)/tail)*guard
                        radius=.9*self.sx
                        d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(*tint,round(gain*220)))
                arrival=end
                if arrival<=time<=arrival+animation['response_ms']:
                    gain=math.sin(math.pi*(time-arrival)/animation['response_ms'])
                    x,y,w,h=project[self.variant]['box']
                    a=self.xy((x,y)); b=self.xy((x+(22 if self.variant=='mobile' else 50),y))
                    d.line([a,b],fill=(*tuple(min(255,c+35) for c in tint),round(gain*140)),width=max(1,round(self.sx*1.5)))
                    x,y=points[-1]; r=1.1*self.sx
                    d.ellipse((x-r,y-r,x+r,y+r),fill=(*tint,round(gain*170)))
        image.alpha_composite(overlay)
        # Invariant edge pixels hide arbitrary independent GIF playback drift.
        band=animation['boundary_freeze']
        for cut in self.cuts:
            box=(cut-band,0,cut+band,self.height)
            image.paste(self.base.crop(box),box[:2])
        return image.convert('RGB')

def save_gif(frames,path):
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=CFG['animation']['frame_ms'],loop=0,disposal=1,optimize=True)

def main():
    animation=CFG['animation']; times=range(0,animation['duration_ms'],animation['frame_ms'])
    if animation['duration_ms']%animation['frame_ms'] or animation['frame_ms']%10:
        raise ValueError('Timeline must have exact GIF centisecond delays and a whole number of frames')
    report={'duration_ms':animation['duration_ms'],'frame_ms':animation['frame_ms'],'variants':{}}
    for variant in ('desktop','mobile'):
        target=OUT/variant; target.mkdir(exist_ok=True)
        # Static rows retain 2× type rendering, independent of the animation palette.
        for row in ('identity','legend','practice','footer'):
            Image.open(OUT/'build'/f'{variant}-{row}.png').save(target/f'{row}.png',optimize=True)
        # A short separate legend would fall below GitHub's 24 px line box on narrow
        # columns. Joining adjacent static rows preserves both pixels and spacing.
        legend=Image.open(OUT/'build'/f'{variant}-legend.png').convert('RGB')
        practice=Image.open(OUT/'build'/f'{variant}-practice.png').convert('RGB')
        combined=Image.new('RGB',(legend.width,legend.height+practice.height),color(CFG['theme']['background']))
        combined.paste(legend,(0,0));combined.paste(practice,(0,legend.height))
        combined.save(target/'practice.png',optimize=True)
        masthead=Image.open(OUT/'build'/f'{variant}-masthead.png')
        for name,start,end in [('brand',0,.7),('github',.7,.85),('linkedin',.85,1)]:
            masthead.crop((round(start*masthead.width),0,round(end*masthead.width),masthead.height)).save(target/f'{name}.png',optimize=True)
        film=Film(variant)
        still=film.frame(0,still=True); still.save(target/'network-static.png',optimize=True)
        sample=Image.new('RGB',(film.width*2,film.height*2))
        for index,time in enumerate((0,2080,4240,5280)):
            sample.paste(film.frame(time),(index%2*film.width,index//2*film.height))
        palette=sample.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
        frames=[]
        for index,time in enumerate(times):
            frames.append(film.frame(time).quantize(palette=palette,dither=Image.Dither.NONE))
        save_gif(frames,target/'network.gif')
        artifacts={}
        for panel in CFG['panels']:
            box=(round(panel['start']*film.width),0,round(panel['end']*film.width),film.height)
            save_gif([f.crop(box) for f in frames],target/f"{panel['id']}.gif")
            still.crop(box).save(target/f"{panel['id']}.png",optimize=True)
            artifacts[panel['id']]=(target/f"{panel['id']}.gif").stat().st_size
        # Complete static hero, also a useful fallback when a GIF cannot be loaded.
        rows=[]
        for row in ('masthead','identity','network','legend','practice','footer'):
            image=still if row=='network' else Image.open(OUT/'build'/f'{variant}-{row}.png').convert('RGB')
            rows.append(image.resize((1120,round(image.height*1120/image.width)),LANCZOS))
        hero=Image.new('RGB',(1120,sum(r.height for r in rows)),color(CFG['theme']['background']))
        y=0
        for row in rows: hero.paste(row,(0,y)); y+=row.height
        hero.save(target/'hero-static.png',optimize=True)
        report['variants'][variant]={'tile_bytes':sum(artifacts.values()),'tiles':artifacts,'width':film.width,'height':film.height,'palette_sha256':hashlib.sha256(bytes(palette.getpalette())).hexdigest()}
        print(f'{variant}: {len(frames)} samples; linked GIFs {sum(artifacts.values()):,} bytes',flush=True)
    (OUT/'animation-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

if __name__=='__main__': main()
