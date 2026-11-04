"""Generate one shared Commit Activity card. Never publishes."""
from pathlib import Path
import argparse
import json
import os
import re
import hashlib
import subprocess
import sys

from activity_data import collect, validate_config, validate_snapshot
from activity_render import card, readme_section
from profile_common import ROOT, MEDIA

CONFIG_PATH = ROOT / 'config/activity.json'
SNAPSHOT = ROOT / 'assets/profile/activity/commits.json'


def load_config():
    return validate_config(json.loads(CONFIG_PATH.read_text(encoding='utf-8')))


def generate(config, data):
    validate_snapshot(data, config)
    files = {SNAPSHOT: json.dumps(data, indent=2, ensure_ascii=False) + '\n'}
    for mobile in (False, True):
        for static in (False, True):
            name = 'activity-commits' + ('-mobile' if mobile else '') + ('-static' if static else '') + '.svg'
            files[MEDIA / name] = card(data, mobile, static)
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    section = readme_section(config)
    pattern = r'<!-- (?:repository-districts|commit-activity):start -->.*?<!-- (?:repository-districts|commit-activity):end -->'
    if '<!-- repository-districts:start -->' in readme or '<!-- commit-activity:start -->' in readme:
        readme, count = re.subn(pattern, lambda _: section, readme, flags=re.S)
        if count != 1:
            raise ValueError('Expected exactly one Commit Activity section')
    else:
        readme = readme.rstrip() + '\n\n' + section + '\n'
    files[ROOT / 'README.md'] = readme
    return files


def export_animations():
    """Rebuild GIFs only when their source or export code changes."""
    from build_profile_assets import build_titles
    build_titles(only={'github-activity'})
    manifest = ROOT/'assets/profile/activity/render.json'
    sources = [MEDIA/'activity-commits.svg', MEDIA/'activity-commits-mobile.svg',
               ROOT/'scripts/render_activity.mjs', ROOT/'scripts/encode_activity.py']
    signature = hashlib.sha256(b''.join(p.read_bytes() for p in sources)).hexdigest()
    outputs = [MEDIA/'activity-commits.gif', MEDIA/'activity-commits-mobile.gif']
    previous = json.loads(manifest.read_text()) if manifest.exists() else {}
    if previous.get('sourceSha256') == signature and all(
            p.exists() and previous.get(p.name) == hashlib.sha256(p.read_bytes()).hexdigest() for p in outputs):
        return []
    subprocess.run(['node', str(ROOT/'scripts/render_activity.mjs')], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT/'scripts/encode_activity.py')], cwd=ROOT, check=True)
    record = {'sourceSha256': signature,
              **{p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in outputs}}
    manifest.write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8', newline='\n')
    return [str(p.relative_to(ROOT)) for p in outputs]+[str(manifest.relative_to(ROOT))]


def build(offline=False):
    config = load_config()
    data = json.loads(SNAPSHOT.read_text(encoding='utf-8')) if offline else collect(config)
    # Complete fetching, validation, and rendering before replacing any published assets.
    files = generate(config, data)
    changed = []
    for path, content in files.items():
        if path.exists() and path.read_text(encoding='utf-8') == content:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + '.tmp')
        temporary.write_text(content, encoding='utf-8', newline='\n')
        os.replace(temporary, path)
        changed.append(str(path.relative_to(ROOT)))
    changed.extend(export_animations())
    # Retire only assets owned by this generator, after the new set is complete.
    for path in MEDIA.glob('activity-*.svg'):
        if path not in files:
            path.unlink()
            changed.append(str(path.relative_to(ROOT)))
    return {'changedFiles': changed, 'window': [data['windowStart'], data['windowEnd']],
            'projects': {p['repo']: p['statistics'] for p in data['projects']}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true', help='Re-render the validated stored snapshot; no network')
    args = parser.parse_args()
    print(json.dumps(build(args.offline), indent=2))


if __name__ == '__main__':
    main()
