"""Build responsive project-table artwork; links remain native README anchors."""
from html import escape
from PIL import Image, ImageOps
from profile_common import CONFIG, ROOT, MEDIA, write_if_changed
from build_profile_assets import font, uri
from build_tech_carousel import icon_uri


def palette(light):
    if light:
        return dict(surface='#ffffff', ink='#1f2328', secondary='#57606a', line='#d0d7de', accent='#ad5552', raised='#f6f8fa')
    p = CONFIG['theme']
    return dict(surface=p['background'], ink=p['text'], secondary=p['secondary'], line=p['line'], accent=p['red'], raised=p['surface'])


def text(x, y, value, size, color, weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(value)}</text>'


def wrap(value, width, size):
    lines = []; current = ''
    for word in value.split():
        candidate = (current + ' ' + word).strip()
        if current and font(size).getlength(candidate) > width:
            lines.append(current); current = word
        else:
            current = candidate
    if current: lines.append(current)
    return lines


def svg(width, height, contents, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">'
            f'<title>{escape(title)}</title><g font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif">{contents}</g></svg>')


def card(project, mobile, light):
    p = palette(light); spec = project['showcase']
    width, height = (288, 476) if mobile else (856, 254)
    parts = [f'<rect width="{width}" height="{height}" fill="{p["surface"]}"/>',
             f'<path d="M1 14V{height-14}" stroke="{p["accent"]}" stroke-width="2"/>']
    photo = Image.open(ROOT / spec['image']).convert('RGB')
    # Preserve the complete real capture, including its original aspect ratio.
    photo = ImageOps.contain(photo, (540, 304), Image.Resampling.LANCZOS)
    photo_width = 252 if mobile else 250
    photo_height = photo_width * photo.height / photo.width
    photo_y = 18 if mobile else 38
    parts.append(f'<image href="{uri(photo)}" x="18" y="{photo_y}" width="{photo_width}" height="{photo_height}"/>')
    parts.append(f'<rect x="18" y="{photo_y}" width="{photo_width}" height="{photo_height}" rx="4" fill="none" stroke="{p["line"]}"/>')
    x = 18 if mobile else 292
    parts.append(text(x, 193 if mobile else 38, project['name'], 26 if mobile else 28, p['ink'], 700))
    parts.append(text(x, 216 if mobile else 63, spec['kind'], 14, p['secondary'], 500))
    for i, line in enumerate(wrap(spec['description'], 252 if mobile else 282, 14 if mobile else 15)):
        parts.append(text(x, (249 if mobile else 100) + i*21, line, 14 if mobile else 15, p['secondary']))
    tag_x = x
    for feature in spec['features']:
        tag_width = round(font(11).getlength(feature)) + 18
        tag_y = 338 if mobile else 216
        parts.append(f'<rect x="{tag_x}" y="{tag_y}" width="{tag_width}" height="24" rx="4" fill="{p["raised"]}" stroke="{p["line"]}"/>')
        parts.append(text(tag_x+9, tag_y+16, feature, 11, p['secondary'], 500))
        tag_x += tag_width + 7
    if mobile:
        parts.append(f'<path d="M18 377H270" stroke="{p["line"]}"/>')
        parts.append(text(18, 399, 'TECH STACK', 11, p['secondary'], 600))
        for i, line in enumerate(wrap(' / '.join(spec['stack']), 250, 13)):
            parts.append(text(18, 420+i*19, line, 13, p['ink'], 500))
        if spec.get('note'): parts.append(text(18, 460, spec['note'], 12, p['secondary']))
    else:
        parts.append(f'<path d="M597 24V230" stroke="{p["line"]}"/>')
        parts.append(text(621, 37, 'TECH STACK', 11, p['secondary'], 600))
        for i, technology in enumerate(spec['stack']):
            parts.append(f'<rect x="621" y="{58+i*30}" width="3" height="3" fill="{p["accent"]}"/>')
            parts.append(text(635, 65+i*30, technology, 14, p['ink'], 500))
        if spec.get('note'): parts.append(text(621, 215, spec['note'], 12, p['secondary']))
    return svg(width, height, ''.join(parts), project['name'] + ' — ' + spec['kind'])


def build_project_table():
    for light in (False, True):
        p = palette(light)
        for mobile in (False, True):
            suffix = ('-mobile' if mobile else '') + ('-light' if light else '')
            for project in CONFIG['projects']:
                write_if_changed(MEDIA / f'project-{project["id"]}{suffix}.svg', card(project, mobile, light))
            width = 288 if mobile else 856
            heading = (f'<rect x=".5" y=".5" width="{width-1}" height="53" fill="{p["raised"]}" stroke="{p["line"]}"/>'
                       + text(18, 35, 'All projects', 22, p['ink'], 650)
                       + text(width-100, 33, f'{len(CONFIG["projects"]):02d} projects', 13, p['secondary'], 500)
                       + f'<path d="M0 0H24M{width-24} 54H{width}" stroke="{p["accent"]}"/>')
            write_if_changed(MEDIA / f'project-table-title{suffix}.svg', svg(width, 54, heading, 'All projects'))
        suffix = '-light' if light else ''
        for disabled in (False, True):
            width = 112 if disabled else 144
            ink = p['secondary'] if disabled else p['ink']
            outline = f'<rect x=".5" y=".5" width="{width-1}" height="43" rx="4" fill="{p["raised"]}" stroke="{p["line"]}"/>'
            if disabled:
                icon = f'<g fill="none" stroke="{ink}" stroke-width="1.5"><path d="M12 22q9-12 18 0-9 12-18 0Z"/><circle cx="21" cy="22" r="3"/></g>'
            else:
                icon = f'<image href="{icon_uri("github",ink)}" x="12" y="13" width="18" height="18"/>'
            contents = outline + icon + text(40, 27, 'Demo' if disabled else 'Repository', 14, ink, 500)
            if not disabled: contents += f'<path d="M124 28l9-10m-8 0h8v8" fill="none" stroke="{ink}" stroke-width="1.2"/>'
            if disabled: contents = f'<g opacity=".55">{contents}</g>'
            name = 'project-demo' if disabled else 'project-repository'
            write_if_changed(MEDIA / f'{name}{suffix}.svg', svg(width, 44, contents, 'Demo — not available yet' if disabled else 'GitHub repository'))
    print(f'Generated responsive project table for {len(CONFIG["projects"])} projects.')


if __name__ == '__main__':
    build_project_table()
