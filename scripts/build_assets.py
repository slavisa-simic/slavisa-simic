"""Prepare the authoritative personal mark and reproducible source manifest."""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/blueprint'

def main():
    for folder in ('source','build','desktop','mobile'):
        (OUT / folder).mkdir(parents=True, exist_ok=True)
    fonts = ROOT / 'assets/source/fonts'
    for source, target in [('Inter.ttf','Inter.ttf'),('OFL.txt','Inter-OFL.txt')]:
        destination = fonts / target
        if not destination.exists():
            shutil.copyfile(ROOT / 'design-explorations/fonts' / source, destination)
    logo = np.array(Image.open(ROOT / 'assets/source/personal-logo.png').convert('RGBA'))
    light = logo[:,:,:3].max(axis=2).astype(np.float32)
    # Only the monochrome logo has a black matte. The source artwork is never overwritten.
    logo[:,:,3] = np.clip((light - 5) / 25 * 255, 0, 255).astype('uint8')
    logo = Image.fromarray(logo)
    logo.crop(logo.getchannel('A').getbbox()).save(OUT / 'source/logo.png', optimize=True)
    paths = [ROOT / 'assets/source/personal-logo.png', *fonts.glob('Inter*'), *fonts.glob('IBMPlexMono*')]
    manifest = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    (OUT / 'source-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Prepared original S logo and licensed fonts.')

if __name__ == '__main__':
    main()
