"""Shared stack data. The hourly README refresh remains standard-library only."""
import json
import base64
from html import escape
from profile_common import ROOT,CONFIG

STACK = json.loads((ROOT / 'config/tech-stack.json').read_text(encoding='utf-8'))


def description():
    return ', '.join(t['name'] + (' (AI development tool)' if t['category'] == 'ai_tool' else '')
                     for t in STACK['technologies'])


def picture(name, alt, width):
    from html import escape
    base = 'assets/profile/generated/' + name
    return (f'<picture><source media="(prefers-color-scheme: light)" srcset="{base}-light.svg">'
            f'<img src="{base}.svg" width="{width}" height="44" alt="{escape(alt, quote=True)}"></picture>')


def carousel_picture(static_for_reduced_motion=True):
    from html import escape
    base = 'assets/profile/generated/tech-carousel'
    sources = []
    # Specific combinations must precede their less-specific fallbacks.
    for mobile, light, reduced in [(True, True, True), (True, False, True),
                                    (False, True, True), (False, False, True),
                                    (True, True, False), (True, False, False), (False, True, False)]:
        if reduced and not static_for_reduced_motion:
            continue
        conditions = []
        if mobile: conditions.append('(max-width: 600px)')
        if light: conditions.append('(prefers-color-scheme: light)')
        if reduced: conditions.append('(prefers-reduced-motion: reduce)')
        suffix = ('-mobile' if mobile else '') + ('-light' if light else '') + ('-reduced' if reduced else '')
        sources.append(f'<source media="{" and ".join(conditions)}" srcset="{base}{suffix}.svg">')
    return ('<picture>' + ''.join(sources) + f'<img src="{base}.svg" width="{STACK["width"]}" '
            f'alt="{escape("Technology stack: " + description(), quote=True)}"></picture>')


def header_assets(avatar_svg, media):
    """Compose responsive headers without altering any pixels or frame geometry.

    Standard-library composition also runs during the hourly avatar refresh.
    """
    avatar_uri = 'data:image/svg+xml;base64,' + base64.b64encode(avatar_svg.encode()).decode()
    files = {}
    for mobile in (False, True):
        for light in (False, True):
            for reduced in (False, True):
                suffix = ('-mobile' if mobile else '') + ('-light' if light else '') + ('-reduced' if reduced else '')
                carousel = (media / f'tech-carousel{suffix}.svg').read_text(encoding='utf-8')
                # Nested SVG keeps the clip, alpha mask and animation self-contained.
                carousel = carousel.replace('<svg ', f'<svg x="{0 if mobile else 208}" y="{202 if mobile else 100}" ', 1)
                tech_height = STACK['height']
                if reduced:
                    import xml.etree.ElementTree as ET
                    tech_height = int(ET.fromstring(carousel).attrib['height'])
                content_width = STACK['mobile_width'] if mobile else STACK['width'] + 208
                width = content_width + (0 if mobile else STACK.get('decoration_right_gutter', 0))
                height = (202 if mobile else 100) + tech_height + 20
                ink = '#1f2328' if light else '#edf0f4'
                secondary = '#57606a' if light else '#c3c8d0'
                name_y, role_y = (150, 179) if mobile else (43, 73)
                text_x = 0 if mobile else 208
                size = 112 if mobile else 176
                decoration = '#57606a' if light else '#edf0f4'
                divider = '' if mobile else (
                           '<path d="M192 10V186" stroke="url(#portrait-line)"/>'
                           '<path d="M192 86V110" stroke="'+decoration+'" stroke-opacity=".75" stroke-width="1.5"/>')
                ornaments = (f'<g fill="none" stroke="{decoration}" stroke-width=".75" stroke-opacity=".25">'
                             f'<path d="M{width-100} 6H{width-4}V28M{width-44} 12H{width-14}"/></g>'
                             f'<path d="M{width-39} 6H{width-21}" fill="none" '
                             f'stroke="{decoration}" stroke-opacity=".65"/>')
                rule_x = 0 if mobile else 208
                rule_y = height - 3
                rule_center = (rule_x + content_width) / 2
                rule = (f'<defs><linearGradient id="contact-rule" gradientUnits="userSpaceOnUse" x1="{rule_x}" y1="{rule_y}" x2="{content_width}" y2="{rule_y}">'
                        f'<stop stop-color="{decoration}" stop-opacity=".12"/><stop offset=".5" stop-color="{decoration}" stop-opacity=".7"/>'
                        f'<stop offset="1" stop-color="{decoration}" stop-opacity=".12"/></linearGradient></defs>'
                        f'<path d="M{rule_x} {rule_y}H{content_width}" stroke="url(#contact-rule)"/>'
                        f'<path d="M{rule_center-26} {rule_y}H{rule_center+26}" stroke="{decoration}" stroke-width="5" stroke-opacity=".08"/>'
                        f'<path d="M{rule_center-26} {rule_y}H{rule_center+26}" stroke="{decoration}" stroke-width="1.8" stroke-opacity=".95"/>')
                svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">'
                       f'<title>{escape(CONFIG["name"])} — Software Engineer</title>'
                       f'<desc>{escape(description())}</desc>'
                       f'<defs><linearGradient id="portrait-line" gradientUnits="userSpaceOnUse" x1="{0 if mobile else 192}" y1="{126 if mobile else 10}" x2="{112 if mobile else 192}" y2="{126 if mobile else 186}">'
                       f'<stop stop-color="{decoration}" stop-opacity=".08"/><stop offset=".5" stop-color="{decoration}" stop-opacity=".5"/>'
                       f'<stop offset="1" stop-color="{decoration}" stop-opacity=".08"/></linearGradient></defs>'
                       + ornaments + f'<g fill="none">{divider}</g>'
                       f'<image href="{avatar_uri}" x="0" y="{0 if mobile else 10}" width="{size}" height="{size}"/>'
                       '<g font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif">'
                       f'<text x="{text_x}" y="{name_y}" font-size="{28 if mobile else 32}" font-weight="600" fill="{ink}">{escape(CONFIG["name"])}</text>'
                       f'<text x="{text_x}" y="{role_y}" font-size="16" fill="{secondary}">Software Engineer</text></g>'
                       + carousel + rule + '</svg>')
                files[media / f'profile-header{suffix}.svg'] = svg
    # Center the independent native links under the information block. The
    # lower-left decoration belongs on this footer row, beside the contacts.
    footer_width = 208 + (STACK['width'] - (160 + 96 + 4)) / 2
    for mobile in (False, True):
        for light in (False, True):
            color = '#57606a' if light else '#edf0f4'
            suffix = ('-mobile' if mobile else '') + ('-light' if light else '')
            ornament = '' if mobile else (
                f'<g fill="none" stroke="{color}" stroke-width=".75" stroke-opacity=".25">'
                '<path d="M1 18V40H91M10 34H43"/></g>'
                f'<path d="M24 40H42" stroke="{color}" stroke-opacity=".65"/>')
            files[media / f'header-spacer{suffix}.svg'] = (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{1 if mobile else footer_width}" height="44">{ornament}</svg>')
    return files


def header_picture():
    # Reuse the exact media selection order of the standalone carousel.
    # Explicit user preference: keep the continuous rightward marquee even
    # when the OS/browser requests reduced motion. Static exports remain available.
    markup = carousel_picture(static_for_reduced_motion=False).replace('tech-carousel', 'profile-header')
    # Natural image dimensions follow the selected source. GitHub's own
    # max-width rule shrinks a composition only when the container needs it.
    markup = markup.replace(f' width="{STACK["width"]}"', '')
    markup = markup.replace('(max-width: 600px)', '(max-width: 768px)')
    original = escape('Technology stack: ' + description(), quote=True)
    alt = escape(CONFIG['name'] + ' — Software Engineer. Technology stack: ' + description(), quote=True)
    return markup.replace(f'alt="{original}"', f'alt="{alt}"')


def spacer():
    base = 'assets/profile/generated/header-spacer'
    return (f'<picture><source media="(max-width: 768px) and (prefers-color-scheme: light)" srcset="{base}-mobile-light.svg">'
            f'<source media="(max-width: 768px)" srcset="{base}-mobile.svg">'
            f'<source media="(prefers-color-scheme: light)" srcset="{base}-light.svg">'
            f'<img src="{base}.svg" height="44" alt=""></picture>')
