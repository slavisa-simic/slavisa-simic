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
    w,h=(480,242) if mobile else (1000,172)
    foreground='#e6edf3' if dark else '#1f2937';muted='#95a3b5' if dark else '#5b6a7e';line='#2b3542' if dark else '#d6deea';bar='#94b0cf' if dark else '#4d729e';empty='#26303c' if dark else '#e0e7f0';surface='#12181f' if dark else '#f7f9fc'
    margin=28 if mobile else 32;chart_x=margin if mobile else 460;chart_right=w-margin;chart_top=150 if mobile else 55;chart_bottom=h-43;chart_h=chart_bottom-chart_top
    gap=6 if mobile else 7;step=(chart_right-chart_x)/len(data['daily']);bw=max(2,step-gap);maximum=max([d['commits'] for d in data['daily']]+[1])
    summary=f"{data['total_commits']} commits · {data['active_days']} active days"
    caption=f"Featured projects · last {data['days']} days"
    elements=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(summary)}</title><desc>{escape(caption)}. Only Vigil and Potamorph repository commits are counted.</desc><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="12" fill="{surface}" stroke="{line}"/>']
    def text(x,y,value,size=14,color=muted,weight=400,anchor='start'):
        return f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{color}" font-family="system-ui,sans-serif" font-size="{size}" font-weight="{weight}">{escape(str(value))}</text>'
    second=256 if mobile else 238;metric_y=82 if mobile else 86;label_y=108 if mobile else 115
    elements += [text(margin,32 if mobile else 34,'FEATURED REPOSITORIES',12),text(margin,metric_y,data['total_commits'],42,foreground,600),text(margin,label_y,'project commits'),text(second,metric_y,data['active_days'],42,foreground,600),text(second,label_y,'active days'),text(chart_x,137 if mobile else 34,f'LAST {data["days"]} DAYS',12)]
    if not mobile:elements.append(f'<path d="M418 32V140" stroke="{line}"/>')
    for i,item in enumerate(data['daily']):
        bh=max(2,round(item['commits']/maximum*chart_h));x=chart_x+i*step
        elements.append(f'<rect x="{x:.2f}" y="{chart_bottom-bh}" width="{bw:.2f}" height="{bh}" rx="1.5" fill="{bar if item["commits"] else empty}"><title>{item["date"]}: {item["commits"]} commits</title></rect>')
    start=datetime.fromisoformat(data['window_start']).strftime('%d %b');end=datetime.fromisoformat(data['window_end']).strftime('%d %b')
    elements += [text(chart_x,h-20,start,12),text(chart_right,h-20,end,12,anchor='end'),'</svg>']
    return ''.join(elements)

def media_picture(name,alt,width='100%',typing=False):
    base='assets/profile/generated'
    if typing:
        sources=f'<source media="(max-width: 600px) and (prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="{base}/identity-mobile-dark.png"><source media="(max-width: 600px) and (prefers-reduced-motion: reduce)" srcset="{base}/identity-mobile-light.png"><source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="{base}/identity-dark.png"><source media="(prefers-reduced-motion: reduce)" srcset="{base}/identity-light.png"><source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="{base}/identity-mobile-dark.svg"><source media="(max-width: 600px)" srcset="{base}/identity-mobile-light.svg"><source media="(prefers-color-scheme: dark)" srcset="{base}/identity-dark.svg">'
        return f'<picture>{sources}<img src="{base}/identity-light.svg" width="860" alt="{escape(alt,quote=True)}"></picture>'
    return f'<picture><source media="(max-width: 600px) and (prefers-reduced-motion: reduce)" srcset="{base}/{name}-mobile-reduced.svg"><source media="(prefers-reduced-motion: reduce)" srcset="{base}/{name}-reduced.svg"><source media="(max-width: 600px)" srcset="{base}/{name}-mobile.svg"><img src="{base}/{name}.svg" width="{width}" alt="{escape(alt,quote=True)}"></picture>'

def render(data):
    identity=media_picture('identity',CONFIG['name']+' — '+' / '.join(CONFIG['roles']),typing=True)
    alt='Projects carousel: '+', '.join(p['name'] for p in CONFIG['projects'])+'. Open the projects list.'
    carousel=f'<p align="center"><a href="{CONFIG["carousel"]["target"]}">{media_picture("projects-carousel",alt,"100%")}</a></p>'
    items=[];notes=[]
    for p in CONFIG['projects']:
        category='Incident management' if p['id']=='vigil' else 'AI development case study'
        items.append(f'<a href="{p["readme"]}"><strong>{escape(p["name"])} &#8599;&#65038;</strong></a> &nbsp; <sub>{category}</sub>')
        notes.append(f'<p><strong>{escape(p["name"])}</strong><br>{escape(p["details"])}</p>')
    projects='<p>'+'<br>'.join(items)+'</p>\n<details><summary>Project notes</summary>'+''.join(notes)+'<p><a href="assets/profile/generated/projects-carousel.png">Static project preview</a></p></details>'
    recent=[]
    for commit in data['recent']:
        message=commit['message']
        if len(message)>72:message=message[:69].rstrip()+'…'
        message=escape(message).replace('|','&#124;').replace('[','&#91;').replace(']','&#93;')
        recent.append(f"- [{message}]({commit['url']})<br><sub>{commit['project_name']} · {commit['date'][:10]}</sub>")
    rows='\n'.join(recent) if recent else 'No project commits in this time window.'
    base='assets/profile/generated'
    stats=f'<picture><source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="{base}/activity-mobile-dark.svg"><source media="(max-width: 600px)" srcset="{base}/activity-mobile-light.svg"><source media="(prefers-color-scheme: dark)" srcset="{base}/activity-dark.svg"><img src="{base}/activity-light.svg" width="900" alt="{data["total_commits"]} project commits across {data["active_days"]} active days in the last {data["days"]} days. Profile automation is excluded."></picture>'
    template=(ROOT/'src/README.template.md').read_text(encoding='utf-8')
    content=template.replace('{{IDENTITY}}',identity).replace('{{INTRO}}',CONFIG['intro']).replace('{{CAROUSEL}}',carousel).replace('{{PROJECTS}}',projects).replace('{{SKILLS}}',' '.join('`'+s+'`' for s in CONFIG['skills'])).replace('{{AI_TOOLS}}',' '.join('`'+s+'`' for s in CONFIG['ai_tools'])).replace('{{ACTIVITY}}',stats).replace('{{RECENT}}',rows).replace('{{SNAPSHOT}}',datetime.fromisoformat(data['fetched_at'].replace('Z','+00:00')).strftime('%d %b %Y')).replace('{{LINKEDIN}}',CONFIG['linkedin'])
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
