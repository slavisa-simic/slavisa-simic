"""Fetch Repository Districts and generate README-compatible assets. Never publishes."""
from pathlib import Path
import argparse
import json
import os
import re

from activity_data import collect, validate_config, validate_snapshot
from activity_render import district, readme_section, slots
from profile_common import ROOT, MEDIA

CONFIG_PATH = ROOT / 'config/activity.json'
SNAPSHOT = ROOT / 'assets/profile/activity/commits.json'


def load_config():
    return validate_config(json.loads(CONFIG_PATH.read_text(encoding='utf-8')))


def generate(config, data):
    validate_snapshot(data, config)
    files = {SNAPSHOT: json.dumps(data, indent=2, ensure_ascii=False) + '\n'}
    peak = max((p['statistics']['maxDailyCommits'] for p in data['projects']), default=1)
    for project in data['projects']:
        stem = 'activity-' + project['repo'].replace('/', '--').lower()
        for mobile in (False, True):
            for static in (False, True):
                name = stem + ('-mobile' if mobile else '') + ('-static' if static else '') + '.svg'
                files[MEDIA / name] = district(project, data, mobile, static, peak)
    for mobile in (False, True):
        image = slots(config, mobile)
        if image:
            files[MEDIA / ('activity-slots' + ('-mobile' if mobile else '') + '.svg')] = image
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    section = readme_section(config)
    pattern = r'<!-- repository-districts:start -->.*?<!-- repository-districts:end -->'
    if '<!-- repository-districts:start -->' in readme:
        readme, count = re.subn(pattern, lambda _: section, readme, flags=re.S)
        if count != 1:
            raise ValueError('Expected exactly one Repository Districts section')
    else:
        readme = readme.rstrip() + '\n\n' + section + '\n'
    files[ROOT / 'README.md'] = readme
    return files


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
