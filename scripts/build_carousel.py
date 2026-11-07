
"""Generate an animated SVG carousel for profile projects."""

from PIL import Image, ImageDraw, ImageOps
from html import escape
import hashlib
import json

from profile_common import ROOT, CONFIG, MEDIA


def draw_slide(project, index, mobile):
    from build_profile_assets import label, LANCZOS

    spec = CONFIG['carousel']
    w = spec['mobile_width'] if mobile else spec['width']
    h = spec['mobile_height'] if mobile else spec['height']

    footer = 48
    body = h - footer
    linoryx = project['id'] == 'linoryx'

    # Linoryx brand palette / Potamorph original palette
    surface = '#F7F5F2' if linoryx else '#152026'
    ink = '#1A1A1A' if linoryx else '#f0e9df'
    muted = '#6B6B6B' if linoryx else '#b4c0bb'

    image = Image.new('RGB', (w, h), surface)
    d = ImageDraw.Draw(image)

    # Background decoration
    if linoryx:
        for gx in range(w // 2, w, 40):
            d.line((gx, 0, gx, body), fill='#E7DED5')

        for gy in range(12, body, 40):
            d.line((w // 2, gy, w, gy), fill='#E7DED5')
    else:
        d.rectangle((0, 0, 5, body), fill='#9e5c51')

    x = 26 if mobile else 44

    label(
        d,
        (x, 22 if mobile else 30),
        f'{index + 1:02d} / {len(CONFIG["projects"]):02d}',
        14,
        muted,
        mono=True
    )

    # Project title and subtitle
    if linoryx:
        label(
            d,
            (x, 60 if mobile else 108),
            'Linoryx',
            48 if mobile else 68,
            ink,
            600
        )
        label(
            d,
            (x, 117 if mobile else 196),
            'Telecom Operations Platform',
            20 if mobile else 24,
            muted,
            450
        )
    else:
        label(
            d,
            (x, 60 if mobile else 108),
            project['name'],
            44 if mobile else 64,
            ink,
            600
        )
        label(
            d,
            (x, 117 if mobile else 196),
            'AI-assisted development case study',
            19 if mobile else 23,
            muted,
            450
        )

    if not mobile:
        d.line(
            (x, 263, x + 50, 263),
            fill=project['accent'],
            width=2
        )

    # Load and proportionally resize project logo
    source = Image.open(ROOT / project['logo']).convert('RGBA')

    visible = source.getchannel('A').point(
        lambda a: 255 if a >= 4 else 0
    ).getbbox()

    if visible is None:
        raise ValueError(f"Logo is transparent: {project['logo']}")

    bounds = (
        max(0, visible[0] - 8),
        max(0, visible[1] - 8),
        min(source.width, visible[2] + 8),
        min(source.height, visible[3] + 8)
    )

    cropped = source.crop(bounds)
    limit = (244, 224) if mobile else (310, 272)
    logo = ImageOps.contain(cropped, limit, LANCZOS)

    cx, cy = (
        (w // 2, body - 133)
        if mobile
        else (w - 224, body // 2 + 3)
    )

    xy = (
        cx - logo.width // 2,
        cy - logo.height // 2
    )

    if linoryx:
        d.rectangle(
            (
                xy[0],
                xy[1],
                xy[0] + logo.width,
                xy[1] + logo.height
            ),
            fill=surface
        )

    image.paste(logo, xy, logo)

    # Footer and frame
    d = ImageDraw.Draw(image)
    p = CONFIG['theme']

    d.rectangle((0, body, w, h), fill=p['background'])
    d.line((0, body, w, body), fill=p['line'])
    d.rectangle(
        (1, 1, w - 2, h - 2),
        outline=p['line'],
        width=2
    )

    record = {
        'file': project['logo'],
        'source_sha256': hashlib.sha256(
            (ROOT / project['logo']).read_bytes()
        ).hexdigest(),
        'crop': list(bounds),
        'position': list(xy),
        'size': list(logo.size),
        'background': surface,
        'operations': [
            'crop near-transparent outer padding',
            'proportional resize',
            'alpha composite'
        ]
    }

    return image, record


def build_carousel():
    from build_profile_assets import uri
    import xml.etree.ElementTree as ET

    spec = CONFIG['carousel']
    report = {}

    hold = spec['hold_ms'] / 1000
    transition = spec['transition_ms'] / 1000
    count = len(CONFIG['projects'])
    duration = count * (hold + transition)

    for mobile in (False, True):
        name = 'projects-carousel' + ('-mobile' if mobile else '')

        slides = []
        logos = []

        for i, project in enumerate(CONFIG['projects']):
            slide, record = draw_slide(project, i, mobile)
            slides.append(slide)
            logos.append(record)

        w, h = slides[0].size
        footer = 48
        body = h - footer

        title = 'Projects carousel — ' + ', '.join(
            p['name'] for p in CONFIG['projects']
        )

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f'<title>{escape(title)}</title>'
            f'<desc>One project at a time. Each project is held for '
            f'three seconds. Open the carousel to reach the projects list.</desc>'
            f'<defs><clipPath id="frame">'
            f'<rect width="{w}" height="{h}"/>'
            f'</clipPath></defs>'
            f'<g clip-path="url(#frame)"><g id="track">'
        ]

        values = ['0 0']
        times = [0]
        splines = []

        for i in range(count):
            values.extend([
                f'{-i * w} 0',
                f'{-(i + 1) * w} 0'
            ])

            times.extend([
                (i * (hold + transition) + hold) / duration,
                (i + 1) * (hold + transition) / duration
            ])

            splines.extend([
                '0 0 1 1',
                '0.22 1 0.36 1'
            ])

        # Place slides horizontally, including a clone of the first.
        for i, slide in enumerate([*slides, slides[0]]):
            encoded = uri(slide.crop((0, 0, w, body)))
            svg.append(
                f'<image href="{encoded}" '
                f'x="{i * w}" width="{w}" height="{body}"/>'
            )

        values_str = ';'.join(values)
        times_str = ';'.join(f'{t:.8f}' for t in times)
        splines_str = ';'.join(splines)

        svg.append(
            f'<animateTransform attributeName="transform" '
            f'type="translate" values="{values_str}" '
            f'keyTimes="{times_str}" keySplines="{splines_str}" '
            f'calcMode="spline" dur="{duration}s" '
            f'repeatCount="indefinite"/></g></g>'
        )

        # Static footer
        footer_image = uri(slides[0].crop((0, body, w, h)))
        svg.append(
            f'<image href="{footer_image}" '
            f'y="{body}" width="{w}" height="{footer}"/>'
        )

        # Active slide indicators
        dot_y = body + 23
        dot_gap = 36
        dot_start = (w - ((count - 1) * dot_gap + 24)) / 2

        switches = [0] + [
            (
                i * (hold + transition)
                + hold
                + transition / 2
            ) / duration
            for i in range(count)
        ] + [1]

        switches_str = ';'.join(f'{t:.8f}' for t in switches)

        for i in range(count):
            x = dot_start + i * dot_gap

            states = (
                [1 if i == 0 else 0]
                + [
                    1 if (j + 1) % count == i else 0
                    for j in range(count)
                ]
                + [1 if i == 0 else 0]
            )

            states_str = ';'.join(map(str, states))

            svg.append(
                f'<rect x="{x}" y="{dot_y}" width="24" height="4" '
                f'rx="2" fill="#46566a"/>'
                f'<rect id="indicator-{i}" x="{x}" y="{dot_y}" '
                f'width="24" height="4" rx="2" fill="#edf2f7" '
                f'opacity="{states[0]}">'
                f'<animate attributeName="opacity" '
                f'values="{states_str}" keyTimes="{switches_str}" '
                f'calcMode="discrete" dur="{duration}s" '
                f'repeatCount="indefinite"/></rect>'
            )

        svg.append(
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" '
            f'fill="none" stroke="{CONFIG["theme"]["line"]}" '
            f'stroke-width="2"/></svg>'
        )

        svg_content = ''.join(svg)

        target = MEDIA / f'{name}.svg'
        target.write_text(
            svg_content,
            encoding='utf-8',
            newline='\n'
        )

        # Static PNG fallback
        static = slides[0].copy()
        d = ImageDraw.Draw(static)

        for i in range(count):
            d.rounded_rectangle(
                (
                    dot_start + i * dot_gap,
                    dot_y,
                    dot_start + i * dot_gap + 24,
                    dot_y + 4
                ),
                2,
                fill='#edf2f7' if i == 0 else '#46566a'
            )

        static.save(MEDIA / f'{name}.png', optimize=True)

        report[name] = {
            'format': 'svg',
            'motion': 'slide',
            'width': w,
            'height': h,
            'bytes': target.stat().st_size,
            'duration_ms': round(duration * 1000),
            'hold_ms': spec['hold_ms'],
            'transition_ms': spec['transition_ms'],
            'projects': [p['id'] for p in CONFIG['projects']],
            'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'logos': logos
        }

        # Reduced motion version
        doc = ET.fromstring(svg_content)
        ns = {'s': 'http://www.w3.org/2000/svg'}

        anim = doc.find('.//s:animateTransform', ns)

        anim.attrib.update({
            'values': ';'.join(
                f'{-i * w} 0' for i in range(count + 1)
            ),
            'keyTimes': ';'.join(
                str(i / count) for i in range(count + 1)
            ),
            'calcMode': 'discrete',
            'dur': f'{count * hold}s'
        })

        anim.attrib.pop('keySplines', None)

        for i, a in enumerate(doc.findall('.//s:animate', ns)):
            a.attrib.update({
                'dur': f'{count * hold}s',
                'keyTimes': ';'.join(
                    str(j / count) for j in range(count + 1)
                ),
                'values': ';'.join(
                    str(int(j % count == i))
                    for j in range(count + 1)
                )
            })

        ET.register_namespace('', 'http://www.w3.org/2000/svg')

        reduced = MEDIA / f'{name}-reduced.svg'
        reduced.write_text(
            ET.tostring(doc, encoding='unicode'),
            encoding='utf-8',
            newline='\n'
        )

        report[name + '-reduced'] = {
            **report[name],
            'motion': 'cut',
            'bytes': reduced.stat().st_size,
            'duration_ms': round(count * hold * 1000),
            'transition_ms': 0,
            'sha256': hashlib.sha256(
                reduced.read_bytes()
            ).hexdigest()
        }

    assert (
        sum(p['bytes'] for p in report.values())
        < spec['total_budget_bytes']
    ), 'Carousel exceeds its media budget'

    manifest = MEDIA / 'media-manifest.json'
    manifest.write_text(
        json.dumps(report, indent=2) + '\n',
        encoding='utf-8',
        newline='\n'
    )

    print(json.dumps({
        name: {
            key: value
            for key, value in item.items()
            if key != 'logos'
        }
        for name, item in report.items()
    }, indent=2))


if __name__ == '__main__':
    build_carousel()
