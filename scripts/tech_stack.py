"""Shared stack data. The hourly README refresh remains standard-library only."""
import json
import base64
import hashlib
from pathlib import Path
from html import escape
from profile_common import ROOT,CONFIG

STACK = json.loads((ROOT / 'config/tech-stack.json').read_text(encoding='utf-8'))


def header_base(avatar_svg):
    # Change the image URL whenever its identity, stack, theme, or layout changes.
    # GitHub's raw-image cache otherwise keeps serving the preceding artwork.
    key = (avatar_svg + json.dumps(STACK, sort_keys=True) + CONFIG['name'] + CONFIG['intro']
           + json.dumps(CONFIG['theme'], sort_keys=True) + Path(__file__).read_text(encoding='utf-8')
           + (ROOT/'scripts/build_tech_carousel.py').read_text(encoding='utf-8'))
    return 'profile-header-' + hashlib.sha256(key.encode()).hexdigest()[:16]


def description():
    return ', '.join(t['name'] + (' (AI development tool)' if t['category'] == 'ai_tool' else '')
                     for t in STACK['technologies'])


def picture(name, alt, width):
    base = 'assets/profile/generated/' + name
    return (f'<picture><source media="(prefers-color-scheme: light)" srcset="{base}-light.svg">'
            f'<img src="{base}.svg" width="{width}" height="44" alt="{escape(alt, quote=True)}"></picture>')


def header_assets(avatar_svg, media):
    """Compose responsive headers without altering any pixels or frame geometry.

    Standard-library composition also runs during the hourly avatar refresh.
    """
    avatar_uri = 'data:image/svg+xml;base64,' + base64.b64encode(avatar_svg.encode()).decode()
    base = header_base(avatar_svg)
    files = {}
    for mobile in (False, True):
        for light in (False, True):
            suffix = ('-mobile' if mobile else '') + ('-light' if light else '')
            carousel = (media / f'tech-carousel{suffix}.svg').read_text(encoding='utf-8')
            # Nested SVG keeps the clip, alpha mask and animation self-contained.
            carousel = carousel.replace('<svg ', f'<svg x="{0 if mobile else 208}" y="{238 if mobile else 138}" ', 1)
            tech_height = STACK['height']
            content_width = STACK['mobile_width'] if mobile else STACK['width'] + 208
            width = content_width + (0 if mobile else STACK.get('decoration_right_gutter', 0))
            height = (238 if mobile else 138) + tech_height + 20
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
                   f'<text x="{text_x}" y="{name_y}" font-size="{28 if mobile else 32}" font-weight="700" fill="{ink}">{escape(CONFIG["name"])}</text>'
                   f'<text x="{text_x}" y="{role_y}" font-size="16" font-weight="500" fill="{secondary}">Software Engineer</text>'
                   f'<text x="{text_x}" y="{role_y+37}" font-size="{14 if mobile else 15}" font-weight="400" fill="{secondary}">Backend &amp; full-stack development.</text></g>'
                   + carousel + rule + '</svg>')
            files[media / f'{base}{suffix}.svg'] = svg
    files.update(about_assets(media))
    # The native links share the identity column on desktop and start at zero
    # in the stacked composition. Switch before the desktop SVG needs scaling.
    footer_width = 208
    for mobile in (False, True):
        for light in (False, True):
            suffix = ('-mobile' if mobile else '') + ('-light' if light else '')
            files[media / f'header-spacer{suffix}.svg'] = (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{1 if mobile else footer_width}" height="44"></svg>')
    return files


def about_assets(media):
    files = {}
    for mobile in (False, True):
        for light in (False, True):
            width, height = (288, 120) if mobile else (856, 64)
            ink = '#1f2328' if light else CONFIG['theme']['text']
            secondary = '#57606a' if light else CONFIG['theme']['secondary']
            line = '#d0d7de' if light else CONFIG['theme']['line']
            surface = '#f6f8fa' if light else CONFIG['theme']['surface']
            red = '#b35b57' if light else CONFIG['theme']['red']
            # Wrap the short description against the compact mobile canvas.
            words = CONFIG['intro'].split(); lines = []; current = ''
            for word in words:
                candidate = (current + ' ' + word).strip()
                if mobile and len(candidate) > 33:
                    lines.append(current); current = word
                else:
                    current = candidate
            if current: lines.append(current)
            text = ''.join(f'<tspan x="{18 if mobile else 244}" y="{68+i*22 if mobile else 38}">{escape(value)}</tspan>' for i, value in enumerate(lines))
            suffix = ('-mobile' if mobile else '') + ('-light' if light else '')
            payload = (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">'
                f'<title>About Me</title><desc>{escape(CONFIG["intro"])}</desc>'
                f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" fill="{surface}" stroke="{line}"/>'
                f'<path d="M16 0H0V14M{width-16} {height}H{width}V{height-14}" fill="none" stroke="{ink}" stroke-opacity=".75"/>'
                f'<path d="M27 23l-7 7 7 7m21-14 7 7-7 7m-8-16-6 19" fill="none" stroke="{red}" stroke-width="1.6"/>'
                f'<g font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif">'
                f'<text x="76" y="37" font-size="20" font-weight="600" fill="{ink}">About Me</text>'
                + ('' if mobile else f'<path d="M214 17v30" stroke="{red}"/>')
                + f'<text font-size="{14 if mobile else 15}" fill="{secondary}">{text}</text></g></svg>')
            # An understated perimeter highlight shares the section titles' six-second rhythm.
            blue = '#5c7da3' if light else CONFIG['theme']['blue']
            route = f'M18 {height-1}H{width-1}V1H1V{height-1}H18'
            motion = (f'<path d="{route}" pathLength="1000" fill="none" stroke="{blue}" stroke-width="1.5" '
                      'stroke-opacity=".85" stroke-dasharray="65 935" stroke-dashoffset="0">'
                      '<animate attributeName="stroke-dashoffset" from="0" to="-1000" dur="6s" repeatCount="indefinite"/></path>')
            files[media / f'about-me-animated{suffix}.svg'] = payload.replace('</svg>',motion+'</svg>')
    return files


def about_picture():
    base = 'assets/profile/generated/about-me-animated'
    return (f'<picture><source media="(max-width: 600px) and (prefers-color-scheme: light)" srcset="{base}-mobile-light.svg">'
            f'<source media="(max-width: 600px)" srcset="{base}-mobile.svg">'
            f'<source media="(prefers-color-scheme: light)" srcset="{base}-light.svg">'
            f'<img src="{base}.svg" width="100%" alt="{escape("About Me. " + CONFIG["intro"], quote=True)}"></picture>')


def header_picture(avatar_svg):
    # Keep the marquee moving in both system motion settings, per user preference.
    base = 'assets/profile/generated/' + header_base(avatar_svg)
    alt = escape(CONFIG['name'] + ' — Software Engineer. Backend & full-stack development. Technology stack: ' + description(), quote=True)
    return (f'<picture><source media="(max-width: 960px) and (prefers-color-scheme: light)" srcset="{base}-mobile-light.svg">'
            f'<source media="(max-width: 960px)" srcset="{base}-mobile.svg">'
            f'<source media="(prefers-color-scheme: light)" srcset="{base}-light.svg">'
            f'<img src="{base}.svg" alt="{alt}"></picture>')


def spacer():
    base = 'assets/profile/generated/header-spacer'
    return (f'<picture><source media="(max-width: 960px) and (prefers-color-scheme: light)" srcset="{base}-mobile-light.svg">'
            f'<source media="(max-width: 960px)" srcset="{base}-mobile.svg">'
            f'<source media="(prefers-color-scheme: light)" srcset="{base}-light.svg">'
            f'<img src="{base}.svg" height="44" alt=""></picture>')
