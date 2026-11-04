"""Check identity boundaries, API traversal, calendar semantics, and published data integrity."""
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
import copy
import json
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import activity_data as data
import activity_render as render
import build_activity as build

NOW = datetime(2026, 11, 4, 12, tzinfo=timezone.utc)


def commit(i, authored='2026-11-03T10:00:00Z', login='slavisa-simic', email='owner@example.com', **extras):
    return {'sha': f'{i:040x}', 'author': {'login': login, 'type': 'User'} if login else None,
            'committer': {'login': 'slavisa-simic', 'type': 'User'},
            'commit': {'author': {'date': authored, 'email': email},
                       'committer': {'date': '2001-01-01T00:00:00Z'}, 'message': 'Implement feature'}, **extras}


class Activity(TestCase):
    def setUp(self):
        # Tests stay independent of the owner's future repository and identity settings.
        self.config = {'periodDays': 365, 'maxProjects': 3, 'timezone': 'UTC',
                       'author': {'logins': ['slavisa-simic'], 'verifiedEmails': [], 'includeBots': False,
                                  'excludedLogins': ['github-actions[bot]'], 'excludedEmails': [],
                                  'excludedMessagePatterns': ['(?i)^\\[automated\\]']},
                       'repositories': [dict(name='Vigil', repo='slavisa-simic/vigil', color='#59A8E8', enabled=True)]}

    def collect(self, commits, config=None):
        def request(path):
            if '?' not in path:
                return {'private': False, 'default_branch': 'main'}
            return commits
        return data.collect(config or self.config, NOW, request)

    def test_identity_matching_ignores_names_bots_and_unrelated_contributors(self):
        self.config['author']['verifiedEmails'] = ['verified@example.com']
        commits = [commit(1), commit(2, login='unrelated'), commit(3, login=None),
                   commit(4, login=None, email='verified@example.com'),
                   commit(5, login='someone-else', email='verified@example.com'),
                   commit(6, login='github-actions[bot]'),
                   commit(7, committer={'login': 'dependabot[bot]', 'type': 'Bot'})]
        automated = commit(8)
        automated['commit']['message'] = '[automated] Update generated assets'
        commits.append(automated)
        project = self.collect(commits)['projects'][0]
        self.assertEqual([c['sha'] for c in project['commits']], [f'{i:040x}' for i in (1, 4)])
        self.config['author']['includeBots'] = True
        self.config['author']['logins'].append('github-actions[bot]')
        self.config['author']['excludedLogins'] = []
        self.assertEqual(self.collect(commits)['projects'][0]['statistics']['totalCommits'], 5)

    def test_author_dates_timezone_window_and_month_ties(self):
        config = copy.deepcopy(self.config)
        config.update(periodDays=3, timezone='Europe/Sarajevo')
        commits = [commit(1, '2026-11-01T23:30:00Z'),  # Nov 2 locally
                   commit(2, '2026-11-03T23:30:00Z'),  # Nov 4 locally
                   commit(3, '2026-11-01T22:59:59Z'),  # outside
                   commit(4, '2026-11-04T23:00:00Z')]  # Nov 5, outside
        project = self.collect(commits, config)['projects'][0]
        self.assertEqual([d['commits'] for d in project['daily']], [1, 0, 1])
        self.assertEqual(project['statistics']['lastCommitDate'], '2026-11-04')
        snapshot = self.collect([commit(1, '2026-10-31T23:00:00Z'), commit(2)])
        self.assertEqual(snapshot['projects'][0]['statistics']['mostActiveMonths'], ['2026-10', '2026-11'])
        data.validate_snapshot(snapshot, self.config)

    def test_pagination_is_pinned_deduplicated_and_not_filtered_by_committer_time(self):
        paths = []
        def request(path):
            paths.append(path)
            if '?' not in path:
                return {'private': False, 'default_branch': 'main'}
            params = parse_qs(urlsplit(path).query)
            self.assertNotIn('since', params)
            self.assertNotIn('until', params)
            if params['page'] == ['1']:
                return [commit(i) for i in range(100)]
            self.assertEqual(params['sha'], [f'{0:040x}'])
            return [commit(99), commit(100, '2025-11-05T00:00:00Z'),
                    commit(101, '2025-11-04T23:59:59Z')]
        snapshot = data.collect(self.config, NOW, request)
        self.assertEqual(len(paths), 3)
        stats = snapshot['projects'][0]['statistics']
        self.assertEqual((stats['totalCommits'], stats['activeDays']), (101, 2))
        self.assertEqual(len(snapshot['projects'][0]['daily']), 365)

    def test_only_vigil_is_initially_enabled_and_empty_slots_have_no_data(self):
        self.assertEqual([r['repo'] for r in self.config['repositories'] if r['enabled']], ['slavisa-simic/vigil'])
        section = render.readme_section(self.config)
        self.assertNotIn('Potamorph', section)
        image = render.slots(self.config)
        self.assertEqual(image.count('Unconfigured</text>'), 2)
        self.assertNotIn('data-commits', image)

    def test_three_independent_repositories_share_height_scale_and_links(self):
        config = copy.deepcopy(self.config)
        config['repositories'] += [dict(name='Second', repo='example/second', color='#B1A2C3', enabled=True),
                                   dict(name='Third', repo='example/third', color='#C3B2A1', enabled=True)]
        def request(path):
            if '?' not in path:
                return {'private': False, 'default_branch': 'main'}
            if '/vigil/' in path:
                return [commit(1)]
            if '/second/' in path:
                return [commit(2), commit(3)]
            return []
        snapshot = data.collect(config, NOW, request)
        self.assertEqual(len(snapshot['projects']), 3)
        self.assertEqual([p['statistics']['totalCommits'] for p in snapshot['projects']], [1, 2, 0])
        self.assertIsNone(render.slots(config))
        for repo in config['repositories']:
            self.assertIn('https://github.com/'+repo['repo'], render.readme_section(config))
        self.assertIn('data-height="32.000000"', render.district(snapshot['projects'][0], snapshot, peak=2))
        config['repositories'][1]['enabled'] = False
        self.assertEqual([p['slot'] for p in self.collect([], config)['projects']], [1, 3])

    def test_empty_repository_and_no_activity_have_zero_metrics(self):
        def request(path):
            if '?' not in path:
                return {'private': False, 'default_branch': 'main'}
            raise HTTPError(path, 409, 'Conflict', {}, BytesIO(b'{"message":"Git Repository is empty."}'))
        snapshot = data.collect(self.config, NOW, request)
        self.assertEqual(snapshot, self.collect([]))
        stats = snapshot['projects'][0]['statistics']
        self.assertEqual((stats['totalCommits'], stats['activeDays']), (0, 0))
        self.assertIsNone(stats['lastCommitDate'])
        self.assertEqual(stats['mostActiveMonths'], [])
        self.assertNotIn('data-height="64.', render.district(snapshot['projects'][0], snapshot))

    def test_private_and_api_errors_never_become_zero_activity(self):
        with self.assertRaisesRegex(ValueError, 'Private'):
            data.collect(self.config, NOW, lambda _: {'private': True})
        error = HTTPError('', 403, 'Forbidden', {}, None)
        self.addCleanup(error.close)
        def forbidden(_):
            raise error
        with self.assertRaises(HTTPError):
            data.collect(self.config, NOW, forbidden)

    def test_invalid_configuration_is_rejected_before_any_request(self):
        for field, value in [('maxProjects', 4), ('periodDays', 0), ('periodDays', True)]:
            config = copy.deepcopy(self.config)
            config[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                data.collect(config, NOW, lambda _: self.fail('Invalid configuration made an API request'))

    def test_all_disabled_projects_make_no_api_requests(self):
        self.config['repositories'][0]['enabled'] = False
        snapshot = data.collect(self.config, NOW, lambda _: self.fail('Disabled project made an API request'))
        self.assertEqual(snapshot['projects'], [])
        self.assertNotIn('data-commits', render.slots(self.config))

    def test_snapshot_metrics_and_scope_are_validated(self):
        snapshot = self.collect([commit(1)])
        snapshot['projects'][0]['statistics']['totalCommits'] += 1
        with self.assertRaisesRegex(ValueError, 'Statistics'):
            data.validate_snapshot(snapshot, self.config)
        snapshot = self.collect([])
        self.config['periodDays'] = 30
        with self.assertRaisesRegex(ValueError, 'Configuration'):
            data.validate_snapshot(snapshot, self.config)

    def test_svg_has_exactly_one_tile_per_day_and_static_fallback(self):
        snapshot = self.collect([commit(1)])
        for mobile in (False, True):
            for static in (False, True):
                image = render.district(snapshot['projects'][0], snapshot, mobile, static)
                tree = ET.fromstring(image)
                cells = tree.findall('.//{http://www.w3.org/2000/svg}g[@data-date]')
                self.assertEqual(len(cells), 365)
                self.assertEqual(sum(int(c.attrib['data-commits']) for c in cells), 1)
                self.assertEqual('repeatCount="indefinite"' in image, not static)
                self.assertNotIn('<script', image)
                self.assertLess(len(image.encode()), 180_000)

    def test_failed_fetch_preserves_files_and_offline_rebuild_is_noop(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'README.md').write_text('Existing profile\n')
            snapshot = root/'snapshot.json'
            media = root/'generated'
            with patch.multiple(build, ROOT=root, MEDIA=media, SNAPSHOT=snapshot), \
                 patch.object(build, 'load_config', return_value=self.config), \
                 patch.object(build, 'collect', return_value=self.collect([commit(1)])):
                self.assertTrue(build.build()['changedFiles'])
                before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob('*') if p.is_file()}
                self.assertEqual(build.build(offline=True)['changedFiles'], [])
                with patch.object(build, 'collect', side_effect=OSError('Unavailable')):
                    with self.assertRaises(OSError):
                        build.build()
                self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in before})

    def test_committed_real_snapshot_is_consistent(self):
        snapshot = json.loads(build.SNAPSHOT.read_text(encoding='utf-8'))
        current = build.load_config()
        if snapshot['configSha256'] != data.fingerprint(current):
            self.skipTest('Configuration has changed; the workflow fetches fresh data after unit tests')
        data.validate_snapshot(snapshot, current)
