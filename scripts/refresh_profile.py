"""Fetch real public project activity and refresh the concise profile. Standard library only."""
from datetime import datetime,timedelta,timezone
from urllib.request import Request,urlopen
from html import escape
from collections import Counter
import argparse
import json
import os
from profile_common import ROOT,CONFIG,OUT,MEDIA,write_if_changed

def api(path):
    headers={'User-Agent':'slavisa-profile-activity','Accept':'application/vnd.github+json'}
    token=os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if token:headers['Authorization']=f'Bearer {token}'
    with urlopen(Request('https://api.github.com'+path,headers=headers),timeout=30) as response:return json.load(response)

def collect(now=None):
    now=now or datetime.now(timezone.utc)
    start=(now-timedelta(days=CONFIG['activity_days']-1)).date()
    end=now.date()
    commits=[];projects=[]
    for project in CONFIG['projects']:
        repository=project['repository']
        if repository.lower()==f"{CONFIG['owner']}/{CONFIG['owner']}".lower():
            raise ValueError('Profile automation must be excluded from project activity')
        meta=api('/repos/'+repository)
        if meta.get('private'):raise ValueError('Public profile activity must not disclose private repositories')
        projects.append({'id':project['id'],'name':project['name'],'repository':repository,'stars':meta['stargazers_count'],'default_branch':meta['default_branch']})
        page=1
        while True:
            batch=api(f'/repos/{repository}/commits?since={start.isoformat()}T00:00:00Z&per_page=100&page={page}')
            for commit in batch:
                date=commit['commit']['committer']['date']
                if start.isoformat()<=date[:10]<=end.isoformat():
                    commits.append({'project':project['id'],'project_name':project['name'],'sha':commit['sha'],'url':commit['html_url'],'date':date,'message':commit['commit']['message'].splitlines()[0]})
            if len(batch)<100:break
            page+=1
    commits.sort(key=lambda c:(c['date'],c['sha']),reverse=True)
    counts=Counter(c['date'][:10] for c in commits)
    daily=[{'date':(start+timedelta(days=i)).isoformat(),'commits':counts[(start+timedelta(days=i)).isoformat()]} for i in range(CONFIG['activity_days'])]
    payload={'scope':'Featured public repositories only; profile automation excluded','window_start':start.isoformat(),'window_end':end.isoformat(),'days':CONFIG['activity_days'],'projects':projects,'total_commits':len(commits),'active_days':len(counts),'daily':daily,'recent':commits[:CONFIG['recent_limit']]}
    previous_path=OUT/'activity.json'
    previous=json.loads(previous_path.read_text(encoding='utf-8')) if previous_path.exists() else None
    if previous and {k:v for k,v in previous.items() if k!='fetched_at'}==payload:
        payload['fetched_at']=previous['fetched_at']
    else:payload['fetched_at']=now.isoformat(timespec='seconds').replace('+00:00','Z')
    return payload

def chart(data,dark,mobile):
    w,h=(360,190) if mobile else (900,166)
    foreground='#e6edf3' if dark else '#1f2328';muted='#9faaba' if dark else '#57606a';line='#303b4a' if dark else '#d5dce5';bar='#82a9d5' if dark else '#356ca8';empty='#202c3a' if dark else '#e8eef5'
    margin=12 if mobile else 20;chart_top=76 if mobile else 55;chart_bottom=h-32;chart_h=chart_bottom-chart_top
    gap=3 if mobile else 7;step=(w-margin*2)/len(data['daily']);bw=max(2,step-gap);maximum=max([d['commits'] for d in data['daily']]+[1])
    summary=f"{data['total_commits']} commits · {data['active_days']} active days"
    caption=f"Featured projects · last {data['days']} days"
    elements=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(summary)}</title><desc>{escape(caption)}. Only Vigil and Potamorph repository commits are counted.</desc>',f'<text x="{margin}" y="25" fill="{foreground}" font-family="system-ui,sans-serif" font-size="{18 if mobile else 21}" font-weight="600">{summary}</text>',f'<text x="{margin}" y="49" fill="{muted}" font-family="system-ui,sans-serif" font-size="{13 if mobile else 13}">{caption}</text>']
    for i,item in enumerate(data['daily']):
        bh=max(2,round(item['commits']/maximum*chart_h));x=margin+i*step
        elements.append(f'<rect x="{x:.2f}" y="{chart_bottom-bh}" width="{bw:.2f}" height="{bh}" rx="1.5" fill="{bar if item["commits"] else empty}"><title>{item["date"]}: {item["commits"]} commits</title></rect>')
    elements += [f'<path d="M{margin} {chart_bottom+3}H{w-margin}" stroke="{line}"/>',f'<text x="{margin}" y="{h-8}" fill="{muted}" font-family="system-ui,sans-serif" font-size="12">{data["window_start"]}</text>',f'<text x="{w-margin}" y="{h-8}" text-anchor="end" fill="{muted}" font-family="system-ui,sans-serif" font-size="12">{data["window_end"]}</text>','</svg>']
    return ''.join(elements)

def media_picture(name,alt,width='100%',typing=False):
    base='assets/profile/generated'
    if typing:
        sources=f'<source media="(max-width: 600px) and (prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="{base}/identity-mobile-dark.png"><source media="(max-width: 600px) and (prefers-reduced-motion: reduce)" srcset="{base}/identity-mobile-light.png"><source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="{base}/identity-dark.png"><source media="(prefers-reduced-motion: reduce)" srcset="{base}/identity-light.png"><source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="{base}/identity-mobile-dark.svg"><source media="(max-width: 600px)" srcset="{base}/identity-mobile-light.svg"><source media="(prefers-color-scheme: dark)" srcset="{base}/identity-dark.svg">'
        return f'<picture>{sources}<img src="{base}/identity-light.svg" width="720" alt="{escape(alt,quote=True)}"></picture>'
    return f'<picture><source media="(max-width: 600px) and (prefers-reduced-motion: reduce)" srcset="{base}/{name}-mobile.png"><source media="(prefers-reduced-motion: reduce)" srcset="{base}/{name}.png"><source media="(max-width: 600px)" srcset="{base}/{name}-mobile.gif"><img src="{base}/{name}.gif" width="{width}" alt="{escape(alt,quote=True)}"></picture>'

def render(data):
    identity=media_picture('identity',CONFIG['name']+' — '+' / '.join(CONFIG['roles']),typing=True)
    cards=[]
    for p in CONFIG['projects']:
        alt=f"{p['name']}: animated project preview. Open the README from the beginning."
        cards.append(f'<a href="{p["readme"]}">{media_picture(p["id"],alt,"100%")}</a>')
    cells=[]
    for p,card in zip(CONFIG['projects'],cards):
        cells.append(f'<td width="50%" valign="top">{card}<p>{escape(p["caption"])}</p><details><summary>{escape(p["details_title"])}</summary><p>{escape(p["details"])}</p></details></td>')
    projects='<table><tr>'+''.join(cells)+'</tr></table>'
    recent=[]
    for commit in data['recent']:
        message=commit['message']
        if len(message)>72:message=message[:69].rstrip()+'…'
        message=escape(message).replace('|','&#124;').replace('[','&#91;').replace(']','&#93;')
        recent.append(f"- [{message}]({commit['url']})<br>\n  <sub>{commit['project_name']} · {commit['date'][:10]}</sub>")
    rows='\n'.join(recent) if recent else 'No project commits in this time window.'
    base='assets/profile/generated'
    stats=f'<picture><source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="{base}/activity-mobile-dark.svg"><source media="(max-width: 600px)" srcset="{base}/activity-mobile-light.svg"><source media="(prefers-color-scheme: dark)" srcset="{base}/activity-dark.svg"><img src="{base}/activity-light.svg" width="900" alt="{data["total_commits"]} project commits across {data["active_days"]} active days in the last {data["days"]} days. Profile automation is excluded."></picture>'
    template=(ROOT/'src/README.template.md').read_text(encoding='utf-8')
    content=template.replace('{{IDENTITY}}',identity).replace('{{INTRO}}',CONFIG['intro']).replace('{{PROJECTS}}',projects).replace('{{SKILLS}}',' · '.join(CONFIG['skills'])).replace('{{AI_TOOLS}}',' · '.join(CONFIG['ai_tools'])).replace('{{ACTIVITY}}',stats).replace('{{RECENT}}',rows).replace('{{SNAPSHOT}}',data['fetched_at'].replace('T',' ').replace('Z',' UTC')).replace('{{LINKEDIN}}',CONFIG['linkedin'])
    return content

def refresh(offline=False):
    # Fetch the entire new snapshot before replacing any valid content.
    data=json.loads((OUT/'activity.json').read_text(encoding='utf-8')) if offline else collect()
    files={OUT/'activity.json':json.dumps(data,indent=2,ensure_ascii=False)+'\n',ROOT/'README.md':render(data)}
    for dark in (False,True):
        for mobile in (False,True):
            name=f'activity{"-mobile" if mobile else ""}-{"dark" if dark else "light"}.svg'
            files[MEDIA/name]=chart(data,dark,mobile)
    OUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True)
    changed=False
    for path,content in files.items():changed=write_if_changed(path,content) or changed
    return {'changed':changed,'snapshot':data['fetched_at'],'commits':data['total_commits'],'active_days':data['active_days'],'repositories':[p['repository'] for p in data['projects']]}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--offline',action='store_true');args=parser.parse_args()
    print(json.dumps(refresh(args.offline),indent=2))

if __name__=='__main__':main()
