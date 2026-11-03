"""Generate the linked, seamless README hero with responsive and reduced-motion sources."""
from pathlib import Path
from html import escape
import json
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config/network.json').read_text(encoding='utf-8'))

def picture(name,width,alt,href=None,animated=False):
    base='assets/blueprint'
    if animated:
        sources=f'<source media="(max-width: 600px) and (prefers-reduced-motion: reduce)" srcset="{base}/mobile/{name}.png"><source media="(max-width: 600px)" srcset="{base}/mobile/{name}.gif"><source media="(prefers-reduced-motion: reduce)" srcset="{base}/desktop/{name}.png">'
        suffix='gif'
    else:
        sources=f'<source media="(max-width: 600px)" srcset="{base}/mobile/{name}.png">'
        suffix='png'
    content=f'<picture>{sources}<img src="{base}/desktop/{name}.{suffix}" width="{width}" align="top" alt="{escape(alt,quote=True)}"></picture>'
    return f'<a href="{escape(href,quote=True)}">{content}</a>' if href else content

def main():
    identity=CFG['identity']
    rows=[
      picture('brand','70%','Slaviša Simić. Open the GitHub profile.',identity['github'])+picture('github','15%','GitHub',identity['github'])+picture('linkedin','15%','Connect on LinkedIn',identity['linkedin']),
      picture('identity','100%',f"{identity['name']} — {identity['role']}. {' '.join(identity['intro'])} Selected work, connected."),
      ''.join(picture(panel['id'],f"{(panel['end']-panel['start'])*100-.00001:.5f}%",panel['alt'],panel['url'],True) for panel in CFG['panels']),
      picture('practice','100%',f"Identity; application; AI case study. Personal skills / Backend engineering: {'; '.join(identity['personal_skills'])}. AI Development Tools: OpenAI Codex. {identity['ai_note']}"),
      picture('footer','100%','Explore the repositories on GitHub.',identity['github']+'?tab=repositories')
    ]
    hero='<p align="center">'+'<br>'.join(rows)+'</p>'
    still=picture('hero-static','100%','Complete static Engineering Blueprint hero with Slaviša Simić, System Core, Vigil, Potamorph AI case study, personal skills, and OpenAI Codex.')
    template=(ROOT/'src/README.template.md').read_text(encoding='utf-8')
    (ROOT/'README.md').write_text(template.replace('{{HERO}}',hero).replace('{{STILL}}',still),encoding='utf-8',newline='\n')
    print('Generated README.md with linked desktop/mobile image panels and native project descriptions.')

if __name__=='__main__': main()
