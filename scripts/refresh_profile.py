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
        project_stats={'id':project['id'],'name':project['name'],'repository':repository,'stars':meta['stargazers_count'],'default_branch':meta['default_branch'],'commits_30d':0}
        projects.append(project_stats)
        page=1
        while True:
            batch=api(f'/repos/{repository}/commits?since={start.isoformat()}T00:00:00Z&per_page=100&page={page}')
            for commit in batch:
                date=commit['commit']['committer']['date']
                if start.isoformat()<=date[:10]<=end.isoformat():
                    project_stats['commits_30d']+=1
                    commits.append({'project':project['id'],'project_name':project['name'],'sha':commit['sha'],'url':commit['html_url'],'date':date,'message':commit['commit']['message'].splitlines()[0]})
            if len(batch)<100:break
            page+=1
    commits.sort(key=lambda c:(c['date'],c['sha']),reverse=True)
    counts=Counter(c['date'][:10] for c in commits)
    daily=[{'date':(start+timedelta(days=i)).isoformat(),'commits':counts[(start+timedelta(days=i)).isoformat()]} for i in range(CONFIG['activity_days'])]
    payload={'scope':'Featured public repositories only; profile automation excluded','window_start':start.isoformat(),'window_end':end.isoformat(),'days':CONFIG['activity_days'],'projects':projects,'total_commits':len(commits),'active_days':len(counts),'daily':daily,'recent':commits[:CONFIG['recent_limit']]}
    payload['fetched_at']=now.isoformat(timespec='seconds').replace('+00:00','Z')
    return payload

def media_picture(name,alt,width='100%'):
    base='assets/profile/generated'
    return f'<picture><source media="(max-width: 600px) and (prefers-reduced-motion: reduce)" srcset="{base}/{name}-mobile-reduced.svg"><source media="(prefers-reduced-motion: reduce)" srcset="{base}/{name}-reduced.svg"><source media="(max-width: 600px)" srcset="{base}/{name}-mobile.svg"><img src="{base}/{name}.svg" width="{width}" alt="{escape(alt,quote=True)}"></picture>'

def render(data):
    identity=f'<p><img src="assets/profile/generated/personal-mark.png" align="right" width="56" height="78" alt="Personal S logo"><samp>{escape(CONFIG["owner"])}@github:~$ whoami</samp></p>\n<h1><samp>{escape(CONFIG["name"])}</samp></h1>\n<p><samp>'+ '<br>'.join(escape(r) for r in CONFIG['roles'])+'</samp></p>'
    alt='Projects carousel: '+', '.join(p['name'] for p in CONFIG['projects'])+'. Open the projects list.'
    carousel=f'<p align="center"><a href="{CONFIG["carousel"]["target"]}">{media_picture("projects-carousel",alt,"100%")}</a></p>'
    items=['<table><thead><tr><th>Project</th><th>Commits<br><sub>30 days</sub></th><th>Stars</th></tr></thead><tbody>'];notes=[]
    by_id={p['id']:p for p in data['projects']}
    for p in CONFIG['projects']:
        live=by_id[p['id']]
        items.append(f'<tr><td><a href="{p["readme"]}"><samp>{escape(p["name"])}</samp></a></td><td align="center"><samp>{live["commits_30d"]}</samp></td><td align="center"><samp>{live["stars"]}</samp></td></tr>')
        notes.append(f'<p><strong>{escape(p["name"])}</strong><br>{escape(p["details"])}</p>')
    sync=datetime.fromisoformat(data['fetched_at'].replace('Z','+00:00')).strftime('%d %b %Y, %H:%M:%S UTC')
    projects=''.join(items)+'</tbody></table>\n'+f'<p><sub>GitHub API · hourly sync · last success {sync}</sub></p>\n<details><summary>Project notes</summary>'+''.join(notes)+'<p><a href="assets/profile/generated/projects-carousel.png">Static project preview</a></p></details>'
    badges=' '.join(f'<img src="assets/profile/badges/{slug}.svg" height="24" alt="{label}">' for slug,label in [('java','Java'),('spring-boot','Spring Boot'),('postgresql','PostgreSQL'),('docker','Docker')])
    ai_badge='<img src="assets/profile/badges/codex.svg" height="24" alt="OpenAI Codex — AI Development Tool">'
    recent=[]
    for commit in data['recent']:
        message=commit['message']
        if len(message)>72:message=message[:69].rstrip()+'…'
        message=escape(message).replace('|','&#124;').replace('[','&#91;').replace(']','&#93;')
        recent.append(f"- [{message}]({commit['url']})<br><sub>{commit['project_name']} · {commit['date'][:10]}</sub>")
    rows='\n'.join(recent) if recent else 'No project commits in this time window.'
    template=(ROOT/'src/README.template.md').read_text(encoding='utf-8')
    content=template.replace('{{IDENTITY}}',identity).replace('{{CAROUSEL}}',carousel).replace('{{PROJECTS}}',projects).replace('{{BADGES}}',badges).replace('{{AI_BADGE}}',ai_badge).replace('{{RECENT}}',rows).replace('{{LINKEDIN}}',CONFIG['linkedin'])
    return content

def refresh(offline=False):
    # Fetch the entire new snapshot before replacing any valid content.
    data=json.loads((OUT/'activity.json').read_text(encoding='utf-8')) if offline else collect()
    files={OUT/'activity.json':json.dumps(data,indent=2,ensure_ascii=False)+'\n',ROOT/'README.md':render(data)}
    OUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True)
    changed=False
    for path,content in files.items():changed=write_if_changed(path,content) or changed
    return {'changed':changed,'snapshot':data['fetched_at'],'commits':data['total_commits'],'active_days':data['active_days'],'repositories':[p['repository'] for p in data['projects']]}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--offline',action='store_true');args=parser.parse_args()
    print(json.dumps(refresh(args.offline),indent=2))

if __name__=='__main__':main()
