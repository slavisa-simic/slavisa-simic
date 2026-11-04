"""Generate a transparent, self-contained SVG marquee. No browser scripts or CSS.

Cached, pinned vendor icons make existing builds work offline. Adding an icon URL
downloads it once; --check-cache verifies the cache without making requests.
"""
import argparse
import base64
import hashlib
import json
import math
import re
from io import BytesIO
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
from profile_common import ROOT, CONFIG, MEDIA, write_if_changed
from build_profile_assets import font
from tech_stack import STACK

ICONS = ROOT / 'assets/profile/icons'
SIMPLE = 'https://raw.githubusercontent.com/simple-icons/simple-icons/13.21.0/'
LINK_ICONS = {
    'github': SIMPLE + 'icons/github.svg',
    'linkedin': SIMPLE + 'icons/linkedin.svg',
}
LICENSES = {
    'Devicon-LICENSE': 'https://raw.githubusercontent.com/devicons/devicon/54cfe13ac10eaa1ef817a343ab0a9437eb3c2e08/LICENSE',
    'Simple-Icons-LICENSE': SIMPLE + 'LICENSE.md',
}


def cached_icons(check_cache=False):
    ICONS.mkdir(parents=True, exist_ok=True)
    path = ICONS / 'provenance.json'
    previous = json.loads(path.read_text()) if path.exists() else {}
    urls = {t['id'] + '.svg': t['icon_url'] for t in STACK['technologies']}
    urls.update({k + '.svg': v for k, v in LINK_ICONS.items()})
    urls.update(LICENSES)
    records = {}
    for name, url in urls.items():
        target = ICONS / name
        old = previous.get(name, {})
        if not target.exists() or old.get('url') != url:
            if check_cache: raise ValueError(f'Missing cached icon or changed URL: {name}')
            if not url.startswith('https://'): raise ValueError('Icon URLs must use HTTPS')
            with urlopen(Request(url, headers={'User-Agent': 'slavisa-profile-assets'}), timeout=30) as response:
                payload = response.read(500_001)
            if len(payload) > 500_000: raise ValueError('Icon exceeds 500 KB')
            if name.endswith('.svg'): safe_svg(payload)
            target.write_bytes(payload)
        payload = target.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if old.get('url') == url and old.get('sha256') != digest:
            raise ValueError(f'Cached icon checksum changed: {name}')
        if name.endswith('.svg'): safe_svg(payload)
        records[name] = {'url': url, 'sha256': digest}
    write_if_changed(path, json.dumps(records, indent=2) + '\n')


def safe_svg(payload):
    svg = ET.fromstring(payload)
    if svg.tag.split('}')[-1] != 'svg' or 'viewBox' not in svg.attrib:
        raise ValueError('Expected an SVG icon with a viewBox')
    for el in svg.iter():
        if el.tag.split('}')[-1] in ('script', 'foreignObject', 'style'):
            raise ValueError('Icon must contain only self-contained vector artwork')
        for key, value in el.attrib.items():
            if key.startswith('on') or (key.endswith('href') and not value.startswith('#')):
                raise ValueError('Icon must not load external content')
    return svg


def data_uri(payload, mime):
    return f'data:{mime};base64,' + base64.b64encode(payload).decode('ascii')


def icon_uri(slug, color=None):
    payload = (ICONS / f'{slug}.svg').read_bytes()
    if color:
        doc = safe_svg(payload)
        doc.set('fill', color)
        payload = ET.tostring(doc, encoding='utf-8')
    return data_uri(payload, 'image/svg+xml')


def label_image(text, size, color, width, height=20):
    # Bundled Inter is rasterized at 2x. No font downloads or OS font differences.
    image = Image.new('RGBA', (width * 2, height * 2))
    draw = ImageDraw.Draw(image)
    draw.text((width, height), text, font=font(size * 2, 450), fill=color, anchor='mm')
    out = BytesIO(); image.save(out, format='PNG', optimize=True)
    return data_uri(out.getvalue(), 'image/png')


def image_tag(uri, x, y, width, height):
    return f'<image href="{uri}" x="{x}" y="{y}" width="{width}" height="{height}"/>'


def layout(spec=None):
    spec = STACK if spec is None else spec
    tech = spec['technologies']
    if not tech: raise ValueError('Add at least one technology')
    ids = [t['id'] for t in tech]
    if len(set(ids)) != len(ids) or not all(re.fullmatch(r'[a-z0-9-]+', i) for i in ids):
        raise ValueError('Technology IDs must be unique lowercase filename slugs')
    if not 1 <= spec['duration_seconds'] <= 300: raise ValueError('Invalid duration')
    if min(spec['width'], spec['mobile_width'], spec['height'], spec['icon_size'], spec['minimum_item_width']) <= 0:
        raise ValueError('Dimensions must be positive')
    longest = max(font(spec['label_size'] * 2, 450).getlength(t['name']) / 2 for t in tech)
    slot = math.ceil(max(spec['minimum_item_width'], longest + 24))
    return slot, slot * len(tech)


def carousel(mobile=False, light=False, reduced=False):
    spec = STACK; tech = spec['technologies']; slot, period = layout()
    width = spec['mobile_width'] if mobile else spec['width']
    height = spec['height']; size = spec['icon_size']
    ink = '#57606a' if light else CONFIG['theme']['secondary']
    columns = min(len(tech), max(1, width // 96)) if mobile else len(tech)
    if reduced: height *= math.ceil(len(tech) / columns)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
           '<title>Technology stack</title><desc>Official logos. Codex is an AI development tool. '
           'Continuous left-to-right motion; reduced motion shows the full stack without movement.</desc>']
    items = []
    for i, t in enumerate(tech):
        x = (i % columns) * width / columns + width / columns / 2 if reduced else i * slot + slot / 2
        y = (i // columns) * spec['height'] if reduced else 0
        color = t.get('light_color', t.get('color')) if light else t.get('color')
        items.append(image_tag(icon_uri(t['id'], color), x - size / 2, y + 8, size, size))
        items.append(image_tag(label_image(t['name'], spec['label_size'], ink, slot), x - slot / 2, y + 47, slot, 20))
    if reduced:
        svg.extend(items)
    else:
        fade = spec['edge_fade']
        svg.append(f'<defs><linearGradient id="fade"><stop offset="0" stop-color="white" stop-opacity="0"/>'
                   f'<stop offset="{fade / width}" stop-color="white"/><stop offset="{1-fade / width}" stop-color="white"/>'
                   '<stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient>'
                   f'<mask id="edges"><rect width="{width}" height="{height}" fill="url(#fade)"/></mask>'
                   f'<g id="sequence">{"".join(items)}</g></defs><g mask="url(#edges)"><g id="tech-track">')
        # The viewport is covered at both endpoints, even with only one item.
        for copy in range(math.ceil(width / period) + 2):
            svg.append(f'<use href="#sequence" x="{copy * period}"/>')
        svg.append(f'<animateTransform attributeName="transform" type="translate" from="{-period} 0" to="0 0" '
                   f'dur="{spec["duration_seconds"]}s" calcMode="linear" repeatCount="indefinite"/></g></g>')
    svg.append('</svg>')
    name = 'tech-carousel' + ('-mobile' if mobile else '') + ('-light' if light else '') + ('-reduced' if reduced else '')
    payload = ''.join(svg)
    write_if_changed(MEDIA / f'{name}.svg', payload)
    return name, {'width': width, 'height': height, 'period': period, 'item_width': slot,
                  'duration_seconds': spec['duration_seconds'], 'direction': 'right', 'static': reduced,
                  'bytes': len(payload.encode()), 'sha256': hashlib.sha256(payload.encode()).hexdigest()}


def link_button(slug, text, width, light):
    ink = '#24292f' if light else CONFIG['theme']['secondary']
    line = '#d0d7de' if light else CONFIG['theme']['line']
    icon_color = '#0A66C2' if slug == 'linkedin' else ink
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="44" viewBox="0 0 {width} 44">'
           f'<rect x="0.5" y="0.5" width="{width-1}" height="43" rx="4" fill="none" stroke="{line}"/>'
           + image_tag(icon_uri(slug, icon_color), 12, 13, 18, 18)
           + image_tag(label_image(text, 12, ink, width - 46, 24), 35, 10, width - 46, 24) + '</svg>')
    write_if_changed(MEDIA / f'link-{slug}{"-light" if light else ""}.svg', svg)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-cache', action='store_true')
    args = parser.parse_args()
    layout(); cached_icons(args.check_cache)
    manifest = {}
    for mobile in (False, True):
        for light in (False, True):
            for reduced in (False, True):
                name, record = carousel(mobile, light, reduced); manifest[name] = record
    for light in (False, True):
        link_button('github', 'GitHub Repositories', 160, light)
        link_button('linkedin', 'LinkedIn', 96, light)
    write_if_changed(MEDIA / 'tech-manifest.json', json.dumps(manifest, indent=2) + '\n')
    # The generated header and README must immediately pick up a changed list.
    from refresh_profile import refresh
    refresh(offline=True)
    print(f'Generated {len(manifest)} tech variants; {len(STACK["technologies"])} technologies, {STACK["duration_seconds"]}s rightward loop.')


if __name__ == '__main__': main()
