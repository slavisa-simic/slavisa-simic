"""Fetch real public project activity and refresh the concise profile. Standard library only."""
from datetime import datetime,timedelta,timezone
from urllib.request import Request,urlopen
from html import escape
from collections import Counter
import argparse
import json
import os
import re
import profile_avatar
from tech_stack import header_assets,header_picture,picture,about_picture,spacer
from profile_common import ROOT,CONFIG,OUT,MEDIA,write_if_changed
from prepare_badges import BADGES
from activity_render import readme_section
from build_activity import load_config as load_activity_config

BADGE_FILES={name:slug for slug,name,_,_ in BADGES}

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

def title(slug,label,level=2):
    base='assets/profile/generated/title-'+slug
    tag=f'h{level}' if level else 'p'
    extension='png'
    if slug in ('projects','github-activity'):base+='-animated';extension='svg'
    return f'<{tag}><picture><source media="(max-width: 600px)" srcset="{base}-mobile.{extension}"><img src="{base}.{extension}" width="100%" alt="{label}"></picture></{tag}>'

def compact_title(slug,label,width):
    path=f'assets/profile/generated/title-{slug}.png'
    # GitHub leaves picture elements unlinked; a summary title must toggle its disclosure.
    return f'<picture><source media="(max-width: 600px)" srcset="{path}"><img src="{path}" width="{width}" height="30" alt="{label}"></picture>'

def render(data,avatar=None):
    avatar=avatar or json.loads((OUT/'avatar.json').read_text(encoding='utf-8'))
    avatar_name,avatar_svg=profile_avatar.frame(avatar,CONFIG['theme'])
    identity=(f'<p>{header_picture(avatar_svg)}</p>\n'
              f'<p>{spacer()}<a href="https://github.com/{CONFIG["owner"]}?tab=repositories">{picture("link-github", "GitHub Repositories", 160)}</a> '
              f'<a href="{escape(CONFIG["linkedin"],quote=True)}">{picture("link-linkedin", "LinkedIn", 96)}</a></p>\n\n'
              f'<p>{about_picture()}</p>')
    alt='Projects carousel: '+', '.join(p['name'] for p in CONFIG['projects'])+'. Open the project table.'
    carousel=f'<p align="center"><a href="{CONFIG["carousel"]["target"]}">{media_picture("projects-carousel",alt,"100%")}</a></p>'
    items=['<table width="100%"><tbody>']
    for p in CONFIG['projects']:
        spec=p['showcase']
        badges=' '.join(f'<img src="assets/profile/badges/{BADGE_FILES[technology]}.svg" height="24" alt="{escape(technology,quote=True)}">' for technology in spec['stack'])
        note=f'<p><sub>{escape(spec["note"])}</sub></p>' if spec.get('note') else ''
        items.append('<tr><td width="25%" align="center" valign="middle">'
                     +f'<img src="assets/profile/generated/project-{p["id"]}-preview.png" width="200" align="middle" alt="{escape(p["name"]+" project screenshot",quote=True)}">'
                     +'</td><td width="35%" align="center" valign="middle">'
                     +f'<p><strong>{escape(p["name"])}</strong></p><p><sub>{escape(spec["kind"])}</sub></p>'
                     +f'<p>{escape(spec["description"])}</p></td><td width="22%" align="center" valign="middle">'
                     +f'<p><strong>Tech stack</strong></p><p>{badges}</p>'+note
                     +'</td><td width="18%" align="center" valign="middle"><p>'
                     +f'<a href="https://github.com/{p["repository"]}">{picture("project-repository",p["name"]+" GitHub repository",144)}</a></p><p>'
                     +picture('project-demo','Demo — not available yet',112)+'</p></td></tr>')
    projects=''.join(items)+'</tbody></table>'
    template=(ROOT/'src/README.template.md').read_text(encoding='utf-8')
    return (template.replace('{{IDENTITY}}',identity).replace('{{CAROUSEL}}',carousel)
            .replace('{{PROJECTS}}',projects).replace('{{PROJECTS_TITLE}}',title('projects','Projects',None))
            .replace('{{ACTIVITY}}',readme_section(load_activity_config()))).rstrip()+'\n'


def refresh(offline=False):
    # Fetch the entire new snapshot before replacing any valid content.
    data=json.loads((OUT/'activity.json').read_text(encoding='utf-8')) if offline else collect()
    avatar=json.loads((OUT/'avatar.json').read_text(encoding='utf-8')) if offline else profile_avatar.fetch(api('/users/'+CONFIG['owner'])['avatar_url'])
    avatar_name,avatar_svg=profile_avatar.frame(avatar,CONFIG['theme'])
    files={OUT/'activity.json':json.dumps(data,indent=2,ensure_ascii=False)+'\n',OUT/'avatar.json':json.dumps(avatar,indent=2)+'\n',MEDIA/avatar_name:avatar_svg,ROOT/'README.md':render(data,avatar)}
    files.update(header_assets(avatar_svg,MEDIA))
    OUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True)
    changed=False
    for path,content in files.items():changed=write_if_changed(path,content) or changed
    # Only retire our own old content-addressed avatar after the replacement exists.
    for previous in MEDIA.glob('profile-avatar-*.svg'):
        if re.fullmatch(r'profile-avatar-[0-9a-f]{16}\.svg',previous.name) and previous.name!=avatar_name:
            previous.unlink();changed=True
    for previous in MEDIA.glob('profile-header*.svg'):
        if re.fullmatch(r'profile-header(?:-[0-9a-f]{16})?(?:-mobile)?(?:-light)?(?:-reduced)?\.svg',previous.name) and previous not in files:
            previous.unlink();changed=True
    return {'changed':changed,'snapshot':data['fetched_at'],'avatar_sha256':avatar['sha256'],'commits':data['total_commits'],'active_days':data['active_days'],'repositories':[p['repository'] for p in data['projects']]}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--offline',action='store_true');args=parser.parse_args()
    print(json.dumps(refresh(args.offline),indent=2))

if __name__=='__main__':main()
