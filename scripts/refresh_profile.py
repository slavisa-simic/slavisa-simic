"""Refresh the public avatar and render the profile README. Standard library only."""
from urllib.request import Request,urlopen
from html import escape
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
    headers={'User-Agent':'slavisa-profile','Accept':'application/vnd.github+json'}
    token=os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if token:headers['Authorization']=f'Bearer {token}'
    with urlopen(Request('https://api.github.com'+path,headers=headers),timeout=30) as response:return json.load(response)

def media_picture(name,alt,width='100%'):
    base='assets/profile/generated'
    return f'<picture><source media="(max-width: 600px) and (prefers-reduced-motion: reduce)" srcset="{base}/{name}-mobile-reduced.svg"><source media="(prefers-reduced-motion: reduce)" srcset="{base}/{name}-reduced.svg"><source media="(max-width: 600px)" srcset="{base}/{name}-mobile.svg"><img src="{base}/{name}.svg" width="{width}" alt="{escape(alt,quote=True)}"></picture>'

def projects_title():
    base='assets/profile/generated/title-projects-animated'
    return f'<p><picture><source media="(max-width: 600px)" srcset="{base}-mobile.svg"><img src="{base}.svg" width="100%" alt="Projects"></picture></p>'

def render(avatar=None):
    avatar=avatar or json.loads((OUT/'avatar.json').read_text(encoding='utf-8'))
    _,avatar_svg=profile_avatar.frame(avatar,CONFIG['theme'])
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
            .replace('{{PROJECTS}}',projects).replace('{{PROJECTS_TITLE}}',projects_title())
            .replace('{{ACTIVITY}}',readme_section(load_activity_config()))).rstrip()+'\n'


def refresh(offline=False):
    # Fetch and render the replacement before touching any published content.
    avatar=json.loads((OUT/'avatar.json').read_text(encoding='utf-8')) if offline else profile_avatar.fetch(api('/users/'+CONFIG['owner'])['avatar_url'])
    avatar_name,avatar_svg=profile_avatar.frame(avatar,CONFIG['theme'])
    files={OUT/'avatar.json':json.dumps(avatar,indent=2)+'\n',MEDIA/avatar_name:avatar_svg,ROOT/'README.md':render(avatar)}
    files.update(header_assets(avatar_svg,MEDIA))
    OUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True)
    changed=False
    for path,content in files.items():changed=write_if_changed(path,content) or changed
    # Only retire our own old content-addressed avatar after the replacement exists.
    for previous in MEDIA.glob('profile-avatar-*.svg'):
        if re.fullmatch(r'profile-avatar-[0-9a-f]{16}\.svg',previous.name) and previous.name!=avatar_name:
            previous.unlink();changed=True
    for previous in MEDIA.glob('profile-header*.svg'):
        if re.fullmatch(r'profile-header-[0-9a-f]{16}(?:-mobile)?(?:-light)?\.svg',previous.name) and previous not in files:
            previous.unlink();changed=True
    return {'changed':changed,'avatar_sha256':avatar['sha256']}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--offline',action='store_true');args=parser.parse_args()
    print(json.dumps(refresh(args.offline),indent=2))

if __name__=='__main__':main()
