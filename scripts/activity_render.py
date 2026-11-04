"""Deterministic isometric SVG images, readable with or without SMIL support."""
from datetime import date
from html import escape
import math

BACKGROUND = '#101113'
LINE = '#292c32'
TEXT = '#edf0f4'
MUTED = '#a4aab5'


def text(x, y, value, size=14, color=MUTED, **attrs):
    extra = ''.join(f' {key.replace("_", "-")}="{escape(str(value), quote=True)}"' for key, value in attrs.items())
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}"{extra}>{escape(str(value))}</text>'


def mix(color, factor):
    return '#' + ''.join(f'{round(int(color[i:i+2], 16) * factor):02x}' for i in (1, 3, 5))


def point(col, row, height=0):
    # True 30-degree isometric ground plane; vertical height is data-only.
    return (384 + (col - row) * 18, 20 + (col + row) * 18 / math.sqrt(3) - height)


def points(values):
    return ' '.join(f'{x:.2f},{y:.2f}' for x, y in values)


def polygon(values, fill, stroke=LINE, **attrs):
    extra = ''.join(f' {key.replace("_", "-")}="{value}"' for key, value in attrs.items())
    return f'<polygon points="{points(values)}" fill="{fill}" stroke="{stroke}" stroke-width="0.7"{extra}/>'


def month_label(months):
    if not months:
        return '—'
    first = date.fromisoformat(months[0] + '-01').strftime('%b %Y')
    return first + (f' (+{len(months)-1} tied)' if len(months) > 1 else '')


def district(project, data, mobile=False, static=False, peak=None):
    width, height = (480, 640) if mobile else (1000, 790)
    accent = project['color']
    stats = project['statistics']
    peak = max(1, peak or stats['maxDailyCommits'])
    rows = 14
    columns = math.ceil(data['periodDays'] / rows)
    # Fit every configured period using the same scale for all project districts.
    fit = min(1, 42 / (columns + rows + 4))
    scale = fit * (.50 if mobile else 1)
    map_y = 200 if mobile else 190
    map_x = width/2 - scale * (384 + (columns-rows)*9)
    title = f"{project['name']} — Repository Commit Activity"
    description = (f"{data['windowStart']} through {data['windowEnd']}, {data['timezone']}. "
                   f"{stats['totalCommits']} commits on {stats['activeDays']} active days. "
                   'Each tile is one calendar day. Read 14 days down each strip, then the next strip. '
                   f'Column height is linear, 64 units at {peak} commits/day. '
                   f"Most active months: {', '.join(stats['mostActiveMonths']) or 'none'}. "
                   f"Latest author date in this period: {stats['lastCommitDate'] or 'none'}. "
                   'These are repository commits, not official GitHub profile contributions.')
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
           f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
           '<defs><pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#22262c" stroke-width="0.6"/></pattern></defs>',
           f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" fill="{BACKGROUND}" stroke="{LINE}"/>',
           f'<rect x="1" y="1" width="{width-2}" height="{height-2}" fill="url(#grid)" opacity=".32"/>',
           f'<path d="M1 25V1H60M{width-60} {height-1}H{width-1}V{height-25}" fill="none" stroke="{accent}" stroke-opacity=".65"/>']
    margin = 24 if mobile else 36
    svg += [text(margin, 34, 'REPOSITORY DISTRICTS', 12, MUTED, letter_spacing='2'),
            text(width-margin, 34, f"{project['slot']:02} / 03", 12, MUTED, text_anchor='end'),
            text(margin, 77 if mobile else 82, project['name'], 32 if mobile else 36, TEXT, font_weight='600'),
            text(width-margin, 76 if mobile else 80, '● CONNECTED', 11, accent, text_anchor='end'),
            text(margin, 108 if mobile else 111, 'Repository Commit Activity', 16, '#c3c8d0'),
            text(margin if mobile else width-margin, 137 if mobile else 109,
                 project['repo'], 12, text_anchor='start' if mobile else 'end')]
    # The font stack is image-contained; no remote fonts, CSS, scripts, or external assets.
    svg.append(text(margin, 160 if mobile else 139,
                    f"{data['windowStart']} — {data['windowEnd']} · {data['timezone']}", 12))
    svg.append(f'<g transform="translate({map_x:.2f} {map_y}) scale({scale:.4f})">')
    a, b, c, d = [point(*p) for p in [(-1, -1), (columns+1, -1), (columns+1, rows+1), (-1, rows+1)]]
    down = lambda p: (p[0], p[1]+6)
    svg += [polygon([d, c, down(c), down(d)], '#121820'),
            polygon([b, c, down(c), down(b)], '#19232d'),
            polygon([a, b, c, d], '#151a20', '#3a434e')]
    # Circuit routing lives outside the data footprint.
    for offset in (0, .28, .56):
        trace = [point(-.8+offset, rows+.4), point(columns*.34, rows+.4),
                 point(columns*.34+.7, rows+.85), point(columns+.65, rows+.85)]
        svg.append(f'<polyline points="{points(trace)}" fill="none" stroke="{accent}" stroke-opacity=".20" stroke-width=".9"/>')
    trace = [point(-.65, -0.65), point(columns+.65, -.65), point(columns+.65, rows+.65)]
    svg.append(f'<polyline points="{points(trace)}" fill="none" stroke="{accent}" stroke-opacity=".4" stroke-width="1.2">')
    if not static:
        svg.append('<animate attributeName="stroke-opacity" values=".25;.6;.25" dur="9s" repeatCount="indefinite"/>')
    svg.append('</polyline>')
    # Back-to-front painter order prevents incorrect face overlap.
    cells = [(i // rows, i % rows, day) for i, day in enumerate(project['daily'])]
    for col, row, day in sorted(cells, key=lambda cell: (sum(cell[:2]), cell[0])):
        count = day['commits']
        h = 64 * count / peak
        pad = .13
        corners = [(col+pad, row+pad), (col+1-pad, row+pad),
                   (col+1-pad, row+1-pad), (col+pad, row+1-pad)]
        top = [point(x, y, h) for x, y in corners]
        floor = [point(x, y) for x, y in corners]
        svg.append(f'<g data-date="{day["date"]}" data-commits="{count}" data-height="{h:.6f}"><title>{day["date"]}: {count} commits</title>')
        if count:
            svg += [polygon([top[3], top[2], floor[2], floor[3]], mix(accent, .40), mix(accent, .54)),
                    polygon([top[1], top[2], floor[2], floor[1]], mix(accent, .58), mix(accent, .68)),
                    polygon(top, mix(accent, .76 + .24*count/peak), mix(accent, .95))]
            if not static and count == stats['maxDailyCommits']:
                svg.append(f'<polygon points="{points(top)}" fill="white" opacity="0"><animate attributeName="opacity" values="0;.12;0" dur="9s" repeatCount="indefinite"/></polygon>')
        else:
            svg.append(polygon(top, '#1c232b', '#303943'))
        svg.append('</g>')
    # Date guides follow the far edge; the partially filled last strip has no extra days.
    for col in range(0, columns, max(1, math.ceil(columns/6))):
        index = col*rows
        x, y = point(col, -1.55)
        svg.append(text(round(x, 1), round(y, 1), project['daily'][index]['date'][5:], 12, MUTED, text_anchor='middle'))
    svg += ['</g>']
    legend_y = 447 if mobile else 664
    svg.append(text(margin, legend_y, f"1 tile = 1 day · 14-day strips · {project['branch']} branch", 12))
    svg.append(text(margin, legend_y+22, f'Height: linear · 0–{peak} commits/day', 12))
    # Four real metrics, with a 2×2 arrangement on phones.
    footer_y = 509 if mobile else 731
    entries = [('COMMITS', stats['totalCommits']), ('ACTIVE DAYS', stats['activeDays']),
               ('MOST ACTIVE MONTH', month_label(stats['mostActiveMonths'])),
               ('LAST COMMIT¹', stats['lastCommitDate'] or '—')]
    svg.append(f'<path d="M{margin} {footer_y-29}H{width-margin}" stroke="{LINE}"/>')
    for i, (label, value) in enumerate(entries):
        x = margin + (i%2)*(width/2) if mobile else margin + i*232
        y = footer_y + (i//2)*57 if mobile else footer_y
        svg.append(text(x, y, label, 10 if mobile else 11, MUTED, letter_spacing='1'))
        svg.append(text(x, y+25, value, 20 if i<2 else 16, TEXT, font_weight='500'))
    svg.append('</svg>')
    result = ''.join(svg)
    return result.replace('<svg xmlns=', '<svg font-family="Inter,Segoe UI,Arial,sans-serif" xmlns=', 1)


def slots(config, mobile=False):
    occupied = {i for i, repo in enumerate(config['repositories'], 1) if repo['enabled']}
    empty = [i for i in range(1, 4) if i not in occupied]
    if not empty:
        return None
    width, height = (480, 68) if mobile else (1000, 68)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="Segoe UI,Arial,sans-serif"><title>Unconfigured repository slots; no activity data</title>']
    for index, slot in enumerate(empty):
        x = index * width/len(empty)
        svg += [f'<rect x="{x+1}" y="1" width="{width/len(empty)-8}" height="60" fill="{BACKGROUND}" stroke="{LINE}" stroke-dasharray="4 5"/>',
                text(x+16, 26, f'DISTRICT {slot:02}', 11, MUTED, letter_spacing='1'),
                text(x+16, 46, 'Unconfigured', 13, '#777f8b')]
    return ''.join(svg) + '</svg>'


def readme_section(config):
    lines = ['<!-- repository-districts:start -->', '<h2>GitHub Activity</h2>',
             '<p><sub>Repository Commit Activity · authored commits, not GitHub profile contributions.</sub></p>']
    for repo in config['repositories']:
        if not repo['enabled']:
            continue
        stem = 'assets/profile/generated/activity-' + repo['repo'].replace('/', '--').lower()
        alt = escape(f"{repo['name']} — Repository Commit Activity. Daily commit towers and period statistics.", quote=True)
        lines.append(f'<p><a href="https://github.com/{escape(repo["repo"], quote=True)}"><picture>'
                     f'<source media="(max-width: 600px) and (prefers-reduced-motion: reduce)" srcset="{stem}-mobile-static.svg">'
                     f'<source media="(prefers-reduced-motion: reduce)" srcset="{stem}-static.svg">'
                     f'<source media="(max-width: 600px)" srcset="{stem}-mobile.svg">'
                     f'<img src="{stem}.svg" width="100%" alt="{alt}"></picture></a></p>')
    if len([repo for repo in config['repositories'] if repo['enabled']]) < 3:
        lines.append('<p><picture><source media="(max-width: 600px)" srcset="assets/profile/generated/activity-slots-mobile.svg">'
                     '<img src="assets/profile/generated/activity-slots.svg" width="100%" alt="Unconfigured repository districts — no activity data"></picture></p>')
    lines += ['<p><sub>¹ Last authored commit within the displayed period. Most active month uses partial months at period boundaries; ties are counted. Each strip reads 14 days back to front, then continues right. Today is partial. '
              '<a href="docs/REPOSITORY_DISTRICTS.md">Data scope &amp; configuration</a> · '
              '<a href="assets/profile/activity/commits.json">Daily data &amp; commit SHAs</a></sub></p>',
              '<!-- repository-districts:end -->']
    return '\n\n'.join(lines)
