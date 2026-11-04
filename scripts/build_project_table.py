"""Build project screenshots and action artwork; project copy stays native text."""
from html import escape
from PIL import Image, ImageOps
from profile_common import CONFIG, ROOT, MEDIA, write_if_changed
from build_tech_carousel import icon_uri


def palette(light):
    if light:
        return dict(ink='#1f2328', secondary='#57606a', line='#d0d7de', raised='#f6f8fa')
    p = CONFIG['theme']
    return dict(ink=p['text'], secondary=p['secondary'], line=p['line'], raised=p['surface'])


def text(x, y, value, size, color, weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(value)}</text>'


def svg(width, height, contents, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">'
            f'<title>{escape(title)}</title><g font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif">{contents}</g></svg>')


def build_project_table():
    for project in CONFIG['projects']:
        photo = Image.open(ROOT / project['showcase']['image']).convert('RGB')
        photo = ImageOps.contain(photo, (600, 338), Image.Resampling.LANCZOS)
        photo.save(MEDIA / f'project-{project["id"]}-preview.png', optimize=True)
    for light in (False, True):
        p = palette(light); suffix = '-light' if light else ''
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
    print(f'Generated screenshots and actions for {len(CONFIG["projects"])} native project rows.')


if __name__ == '__main__':
    build_project_table()
