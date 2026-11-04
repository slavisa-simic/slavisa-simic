"""One shared isometric commit timeline with project-colored, additive daily columns."""
from datetime import date, timedelta
from html import escape
import math

BACKGROUND = '#101113'
LINE = '#292c32'
TEXT = '#edf0f4'
MUTED = '#a4aab5'
LOOP_SECONDS = 6


def text(x, y, value, size=14, color=MUTED, **attrs):
    extra = ''.join(f' {key.replace("_", "-")}="{escape(str(value), quote=True)}"' for key, value in attrs.items())
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}"{extra}>{escape(str(value))}</text>'


def mix(color, factor):
    return '#' + ''.join(f'{round(int(color[i:i+2], 16) * factor):02x}' for i in (1, 3, 5))


def point(col, row, height=0):
    return (384 + (col-row)*18, 20 + (col+row)*18/math.sqrt(3) - height)


def points(values):
    return ' '.join(f'{x:.2f},{y:.2f}' for x, y in values)


def polygon(values, fill, stroke=LINE):
    return f'<polygon points="{points(values)}" fill="{fill}" stroke="{stroke}" stroke-width=".7"/>'


def month_label(months):
    if not months:
        return '—'
    first = date.fromisoformat(months[0]+'-01').strftime('%b %Y')
    return first + (f' (+{len(months)-1})' if len(months)>1 else '')


def timeline(data):
    start = date.fromisoformat(data['windowStart'])
    return [{'date': (start+timedelta(days=i)).isoformat(),
             'counts': [p['daily'][i]['commits'] for p in data['projects']]}
            for i in range(data['periodDays'])]


def card(data, mobile=False, static=False):
    projects = data['projects']
    days = timeline(data)
    peak = max(1, max(sum(day['counts']) for day in days))
    width = 480 if mobile else 1000
    height = (460+100*len(projects)) if mobile else (702+42*len(projects))
    margin = 24 if mobile else 36
    rows = 14
    columns = math.ceil(data['periodDays']/rows)
    scale = min(1, 42/(columns+rows+4)) * (.5 if mobile else 1)
    map_x = width/2 - scale*(384+(columns-rows)*9)
    map_y = 155
    summary = '; '.join(f"{p['name']}: {p['statistics']['totalCommits']} commits, {p['statistics']['activeDays']} active days" for p in projects)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="Inter,Segoe UI,Arial,sans-serif" role="img" aria-labelledby="title desc">',
           '<title id="title">Repository Commit Activity</title>',
           f'<desc id="desc">{escape(summary)}. {data["windowStart"]} through {data["windowEnd"]}, {escape(data["timezone"])}. One tile per calendar day; colored segments add to the daily total. Height is linear, 64 units at {peak} commits/day. Author-filtered repository commits, not GitHub profile contributions.</desc>',
           '<defs><pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#22262c" stroke-width=".6"/></pattern></defs>',
           f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" fill="{BACKGROUND}" stroke="{LINE}"/>',
           f'<rect x="1" y="1" width="{width-2}" height="{height-2}" fill="url(#grid)" opacity=".32"/>',
           '<path d="M1 25V1H55" fill="none" stroke="#59A8E8"/>',
           f'<path d="M{width-55} {height-1}H{width-1}V{height-25}" fill="none" stroke="#CC8A88"/>',
           text(margin, 42, 'Repository Commit Activity', 22 if mobile else 26, TEXT, font_weight='550'),
           text(margin, 69, f"{data['windowStart']} — {data['windowEnd']} · {data['timezone']}", 12)]
    for i, project in enumerate(projects):
        x = margin+i*(145 if mobile else 190)
        svg += [f'<rect x="{x}" y="91" width="8" height="8" fill="{project["color"]}"/>',
                text(x+16, 99, project['name'], 13, '#c3c8d0')]
    svg.append(f'<g transform="translate({map_x:.2f} {map_y}) scale({scale:.4f})">')
    a, b, c, d = [point(*p) for p in [(-1,-1), (columns+1,-1), (columns+1,rows+1), (-1,rows+1)]]
    down = lambda p: (p[0],p[1]+6)
    svg += [polygon([d,c,down(c),down(d)], '#121820'),
            polygon([b,c,down(c),down(b)], '#19232d'),
            polygon([a,b,c,d], '#151a20', '#3a434e')]
    for i, project in enumerate(projects):
        offset = .2+i*.24
        route = [point(-1+offset,-1+offset), point(columns+1-offset,-1+offset),
                 point(columns+1-offset,rows+1-offset), point(-1+offset,rows+1-offset)]
        path = 'M'+'L'.join(f'{x:.2f} {y:.2f}' for x,y in route)+'Z'
        svg.append(f'<path d="{path}" fill="none" stroke="{project["color"]}" stroke-opacity=".22" stroke-width="1.2"/>')
        if not static:
            svg.append(f'<path d="{path}" pathLength="1000" fill="none" stroke="{project["color"]}" stroke-width="3" stroke-linecap="round" stroke-dasharray="80 920" stroke-dashoffset="{i*330}" opacity=".95"><animate attributeName="stroke-dashoffset" from="{i*330}" to="{i*330-1000}" dur="6s" repeatCount="indefinite"/></path>')
    cells = [(i//rows,i%rows,day) for i,day in enumerate(days)]
    for col,row,day in sorted(cells,key=lambda cell:(cell[0]+cell[1],cell[0])):
        total = sum(day['counts'])
        svg.append(f'<g data-date="{day["date"]}" data-total-commits="{total}"><title>{day["date"]}: {total} commits</title>')
        corners = [(col+.13,row+.13),(col+.87,row+.13),(col+.87,row+.87),(col+.13,row+.87)]
        floor = [point(x,y) for x,y in corners]
        if not total:
            svg.append(polygon(floor,'#1c232b','#303943'))
        cumulative = 0
        for project,count in zip(projects,day['counts']):
            if not count:
                continue
            low = 64*cumulative/peak
            high = 64*(cumulative+count)/peak
            bottom = [point(x,y,low) for x,y in corners]
            top = [point(x,y,high) for x,y in corners]
            color = project['color']
            svg.append(f'<g data-project="{escape(project["repo"],quote=True)}" data-commits="{count}" data-height="{high-low:.6f}">')
            svg += [polygon([top[3],top[2],bottom[2],bottom[3]],mix(color,.45),mix(color,.65)),
                    polygon([top[1],top[2],bottom[2],bottom[1]],mix(color,.65),mix(color,.83)),
                    polygon(top,color,mix(color,.98))]
            if not static:
                svg.append(f'<polygon points="{points(top)}" fill="white" opacity=".04"><animate attributeName="opacity" values=".04;.32;.04" dur="6s" repeatCount="indefinite"/></polygon>')
            svg.append('</g>')
            cumulative += count
        svg.append('</g>')
    for col in range(0,columns,max(1,math.ceil(columns/6))):
        x,y = point(col,-1.55)
        svg.append(text(round(x,1),round(y,1),days[col*rows]['date'][5:],12,MUTED,text_anchor='middle'))
    svg.append('</g>')
    svg.append(text(margin,406 if mobile else 627,f'1 day / tile · 0–{peak} commits/day',12))
    if mobile:
        for i,p in enumerate(projects):
            y = 451+i*100
            stats = p['statistics']
            svg += [f'<path d="M{margin} {y-20}H{width-margin}" stroke="{LINE}"/>',
                    text(margin,y,p['name'],16,p['color'],font_weight='550'),
                    text(width-margin,y,f"{stats['totalCommits']} commits · {stats['activeDays']} active days",12,TEXT,text_anchor='end'),
                    text(margin,y+28,'PEAK MONTH',10),text(270,y+28,'LAST COMMIT',10),
                    text(margin,y+49,month_label(stats['mostActiveMonths']),15,TEXT),
                    text(270,y+49,stats['lastCommitDate'] or '—',15,TEXT)]
    else:
        svg.append(f'<path d="M{margin} 649H{width-margin}" stroke="{LINE}"/>')
        for x,label in [(36,'PROJECT'),(280,'COMMITS'),(425,'ACTIVE DAYS'),(600,'PEAK MONTH'),(810,'LAST COMMIT')]:
            svg.append(text(x,674,label,11))
        for i,p in enumerate(projects):
            y = 707+i*42
            stats = p['statistics']
            for x,value,color in [(36,p['name'],p['color']),(280,stats['totalCommits'],TEXT),
                                   (425,stats['activeDays'],TEXT),(600,month_label(stats['mostActiveMonths']),TEXT),
                                   (810,stats['lastCommitDate'] or '—',TEXT)]:
                svg.append(text(x,y,value,16,color))
    svg.append('</svg>')
    return ''.join(svg)


def readme_section(config):
    base = 'assets/profile/generated/'
    title = (f'<p><picture><source media="(max-width: 600px)" srcset="{base}title-github-activity-animated-mobile.svg">'
             f'<img src="{base}title-github-activity-animated.svg" width="100%" alt="GitHub Activity"></picture></p>')
    image = (f'<p><picture><source media="(max-width: 600px)" srcset="{base}activity-commits-mobile.gif">'
             f'<img src="{base}activity-commits.gif" width="100%" alt="Repository Commit Activity — daily commits colored by project"></picture></p>')
    links = ' · '.join(f'<a href="https://github.com/{escape(p["repo"],quote=True)}">{escape(p["name"])}</a>'
                       for p in config['repositories'] if p['enabled'])
    return '\n\n'.join(['<!-- commit-activity:start -->',title,image,f'<p><sub>{links}</sub></p>','<!-- commit-activity:end -->'])
