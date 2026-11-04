"""Collect public, author-attributed repository commits; no third-party dependencies."""
from collections import Counter
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import json
import os
import re
import time


def validate_config(config):
    if config.get('maxProjects') != 3:
        raise ValueError('Repository Districts has exactly three available slots')
    if type(config.get('periodDays')) is not int or not 1 <= config['periodDays'] <= 3660:
        raise ValueError('periodDays must be an integer from 1 to 3660')
    ZoneInfo(config['timezone'])
    repositories = config['repositories']
    if len(repositories) > 3:
        raise ValueError('At most three repositories can be configured')
    seen = set()
    for repo in repositories:
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo['repo']):
            raise ValueError('Expected owner/repository')
        if repo['repo'].lower() in seen:
            raise ValueError('Duplicate repository')
        seen.add(repo['repo'].lower())
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', repo['color']):
            raise ValueError('Accent must be a six-digit hex color')
        if not isinstance(repo['name'], str) or not 1 <= len(repo['name']) <= 40:
            raise ValueError('Project name must contain 1–40 characters')
        if type(repo['enabled']) is not bool:
            raise ValueError('enabled must be a boolean')
    author = config['author']
    if not author['logins'] and not author['verifiedEmails']:
        raise ValueError('Configure at least one author identity')
    for pattern in author.get('excludedMessagePatterns', []):
        re.compile(pattern)
    return config


def fingerprint(config):
    return sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()


def api(path):
    """Credentials are sent only to the fixed GitHub API origin. Fail closed on errors."""
    if not path.startswith('/repos/'):
        raise ValueError('Only repository API endpoints are allowed')
    headers = {'User-Agent': 'repository-districts', 'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2026-03-10'}
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    for attempt in range(3):
        try:
            with urlopen(Request('https://api.github.com' + path, headers=headers), timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
            time.sleep(min(10, int(error.headers.get('Retry-After', '2'))))


def matches_author(commit, author):
    linked = commit.get('author') or {}
    login = linked.get('login', '').lower()
    committer = commit.get('committer') or {}
    email = commit['commit']['author'].get('email', '').lower()
    if not author.get('includeBots', False):
        # Automated commits made via bot committers are excluded too.
        if any(person.get('type') == 'Bot' or person.get('login', '').lower().endswith('[bot]')
               for person in (linked, committer)) or '[bot]' in email:
            return False
        if any(re.search(pattern, commit['commit']['message'])
               for pattern in author.get('excludedMessagePatterns', [])):
            return False
    if login in {value.lower() for value in author.get('excludedLogins', [])}:
        return False
    if email in {value.lower() for value in author.get('excludedEmails', [])}:
        return False
    if login in {value.lower() for value in author['logins']}:
        return True
    # Email mappings are an explicit owner assertion, never inferred from display names.
    # A conflicting linked account takes precedence over an email mapping.
    return not login and email in {value.lower() for value in author['verifiedEmails']}


def statistics(daily):
    months = Counter()
    for day in daily:
        months[day['date'][:7]] += day['commits']
    peak = max(months.values(), default=0)
    return {'totalCommits': sum(day['commits'] for day in daily),
            'activeDays': sum(day['commits'] > 0 for day in daily),
            'mostActiveMonths': sorted(month for month, count in months.items() if count == peak) if peak else [],
            'mostActiveMonthCommits': peak,
            'lastCommitDate': max((day['date'] for day in daily if day['commits']), default=None),
            'maxDailyCommits': max((day['commits'] for day in daily), default=0)}


def collect(config, now=None, request=api):
    validate_config(config)
    now = now or datetime.now(timezone.utc)
    zone = ZoneInfo(config['timezone'])
    end = now.astimezone(zone).date()
    start = end - timedelta(days=config['periodDays'] - 1)
    projects = []
    for slot, repo in enumerate(config['repositories'], 1):
        if not repo['enabled']:
            continue
        base = '/repos/' + repo['repo']
        meta = request(base)
        if meta.get('private'):
            raise ValueError('Private repository activity cannot be published')
        branch = repo.get('branch') or meta['default_branch']
        head = None
        commits = {}
        page = 1
        while True:
            # Pin the first returned SHA for subsequent pages: new pushes cannot shift pages.
            query = urlencode({'sha': head or branch, 'per_page': 100, 'page': page})
            try:
                batch = request(base + '/commits?' + query)
            except HTTPError as error:
                # A truly empty Git repository returns 409. Other conflicts are failures.
                if page == 1 and error.code == 409 and 'Git Repository is empty' in error.read().decode():
                    error.close()
                    batch = []
                else:
                    raise
            if not isinstance(batch, list):
                raise ValueError('Expected a GitHub commits array')
            if batch and head is None:
                head = batch[0]['sha']
            for commit in batch:
                if not matches_author(commit, config['author']):
                    continue
                authored = datetime.fromisoformat(commit['commit']['author']['date'].replace('Z', '+00:00'))
                if authored.tzinfo is None:
                    raise ValueError('Commit date has no timezone')
                date = authored.astimezone(zone).date()
                if start <= date <= end:
                    commits[commit['sha']] = {'sha': commit['sha'], 'date': date.isoformat(),
                                              'authoredAt': authored.isoformat()}
            if len(batch) < 100:
                break
            page += 1
        counts = Counter(commit['date'] for commit in commits.values())
        daily = [{'date': (start + timedelta(days=i)).isoformat(),
                  'commits': counts[(start + timedelta(days=i)).isoformat()]}
                 for i in range(config['periodDays'])]
        projects.append({**repo, 'slot': slot, 'branch': branch, 'headSha': head,
                         'commits': sorted(commits.values(), key=lambda c: (c['date'], c['sha'])),
                         'daily': daily, 'statistics': statistics(daily)})
    # No fetch timestamp: identical inputs on the same calendar day produce identical bytes.
    return {'schemaVersion': 1, 'configSha256': fingerprint(config),
            'label': 'Repository Commit Activity', 'dateField': 'commit.author.date',
            'scope': 'Unique commits reachable from the selected branch, authored by configured identities; merge commits included',
            'timezone': config['timezone'], 'periodDays': config['periodDays'],
            'windowStart': start.isoformat(), 'windowEnd': end.isoformat(), 'projects': projects}


def validate_snapshot(data, config):
    """Offline rendering must not silently reuse another scope or inconsistent metrics."""
    validate_config(config)
    if data['configSha256'] != fingerprint(config):
        raise ValueError('Configuration changed; fetch a fresh snapshot before rendering')
    if (data['schemaVersion'], data['timezone'], data['periodDays'], data['dateField']) != (
            1, config['timezone'], config['periodDays'], 'commit.author.date'):
        raise ValueError('Snapshot calendar or schema mismatch')
    expected = [(i, r['repo']) for i, r in enumerate(config['repositories'], 1) if r['enabled']]
    if [(p['slot'], p['repo']) for p in data['projects']] != expected:
        raise ValueError('Snapshot repository scope mismatch')
    start = datetime.fromisoformat(data['windowStart']).date()
    dates = [(start + timedelta(days=i)).isoformat() for i in range(config['periodDays'])]
    if dates[-1] != data['windowEnd']:
        raise ValueError('Snapshot date range mismatch')
    for project in data['projects']:
        repo = config['repositories'][project['slot']-1]
        if any(project[key] != repo[key] for key in ('name', 'color', 'repo', 'enabled')):
            raise ValueError('Snapshot project configuration mismatch')
        counts = Counter(c['date'] for c in project['commits'])
        zone = ZoneInfo(config['timezone'])
        if any(datetime.fromisoformat(c['authoredAt']).astimezone(zone).date().isoformat() != c['date']
               for c in project['commits']):
            raise ValueError('Commit calendar date does not match its author timestamp')
        if len({c['sha'] for c in project['commits']}) != len(project['commits']):
            raise ValueError('Duplicate commit SHA')
        if project['daily'] != [{'date': date, 'commits': counts[date]} for date in dates]:
            raise ValueError('Daily activity does not match commit records')
        if sum(counts.values()) != sum(d['commits'] for d in project['daily']):
            raise ValueError('Commit outside snapshot window')
        if project['statistics'] != statistics(project['daily']):
            raise ValueError('Statistics do not match daily activity')
