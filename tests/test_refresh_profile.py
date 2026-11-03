"""Exercise public data boundaries and preservation of the last good profile."""
from datetime import datetime,timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase,main
from unittest.mock import patch
import copy
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import refresh_profile as profile

NOW=datetime(2026,11,3,12,tzinfo=timezone.utc)

def commit(index,date='2026-11-03T10:00:00Z',message='Improve project'):
    return {'sha':f'{index:040x}','html_url':f'https://github.com/example/project/commit/{index:040x}',
            'commit':{'committer':{'date':date},'message':message}}

class ActivityRefresh(TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.out=self.root/'activity';self.out.mkdir()
        self.config=copy.deepcopy(profile.CONFIG)
        for key,value in {'ROOT':self.root,'OUT':self.out,'MEDIA':self.out/'generated','CONFIG':self.config}.items():
            patcher=patch.object(profile,key,value);patcher.start();self.addCleanup(patcher.stop)
        (self.root/'src').mkdir()
        original=Path(__file__).resolve().parents[1]/'src/README.template.md'
        (self.root/'src/README.template.md').write_text(original.read_text(encoding='utf-8'),encoding='utf-8')

    def api(self,path):
        if '?' not in path:return {'private':False,'stargazers_count':2,'default_branch':'main'}
        return []

    def collect(self,api=None):
        with patch.object(profile,'api',side_effect=api or self.api):return profile.collect(NOW)

    def test_pagination_counts_window_and_repository_scope(self):
        paths=[]
        def api(path):
            paths.append(path)
            if '?' not in path:return self.api(path)
            if '/vigil/' not in path:return [commit(200,'2026-10-05T00:00:00Z'),commit(201,'2026-10-04T23:59:59Z'),commit(202,'2026-11-04T00:00:00Z')]
            if '&page=1' in path:return [commit(i) for i in range(100)]
            return [commit(100,'2026-11-02T10:00:00Z')]
        data=self.collect(api)
        self.assertEqual(data['total_commits'],102)
        self.assertEqual(data['active_days'],3)
        self.assertEqual(sum(day['commits'] for day in data['daily']),102)
        self.assertEqual(len(data['daily']),30)
        self.assertEqual(len(data['recent']),3)
        self.assertEqual({p['id']:p['commits_30d'] for p in data['projects']},{'vigil':101,'potamorph':1})
        self.assertTrue(any('page=2' in path for path in paths))
        self.assertTrue(all('/repos/slavisa-simic/slavisa-simic' not in path for path in paths))

    def test_successful_sync_updates_time_and_offline_rebuild_is_noop(self):
        data=self.collect();data['fetched_at']='2026-11-03T01:00:00Z'
        (self.out/'activity.json').write_text(json.dumps(data),encoding='utf-8')
        with patch.object(profile,'api',side_effect=self.api):
            fresh=profile.collect(NOW)
        self.assertEqual(fresh['fetched_at'],'2026-11-03T12:00:00Z')
        self.assertNotEqual(fresh['fetched_at'],data['fetched_at'])
        profile.refresh(offline=True)
        before={p:p.stat().st_mtime_ns for p in self.root.rglob('*') if p.is_file()}
        self.assertFalse(profile.refresh(offline=True)['changed'])
        self.assertEqual(before,{p:p.stat().st_mtime_ns for p in before})

    def test_partial_api_failure_preserves_every_published_file(self):
        (self.out/'activity.json').write_text(json.dumps(self.collect()),encoding='utf-8')
        profile.refresh(offline=True)
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        def fail_second_repository(path):
            if '/tower-defense-ai' in path:raise OSError('API unavailable')
            return self.api(path)
        with patch.object(profile,'api',side_effect=fail_second_repository),self.assertRaises(OSError):profile.refresh()
        self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_private_repository_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'private'):
            self.collect(lambda path:{'private':True})

    def test_profile_automation_cannot_become_project_activity(self):
        self.config['projects'][0]['repository']='slavisa-simic/slavisa-simic'
        with self.assertRaisesRegex(ValueError,'automation'):self.collect()

    def test_commit_messages_cannot_inject_markup_or_links(self):
        data=self.collect();data['recent']=[{'message':'<img src=x> [fake](https://bad.example) & fix','project_name':'Vigil','date':'2026-11-03','url':'https://github.com/example/project/commit/123'}]
        readme=profile.render(data)
        self.assertNotIn('<img src=x>',readme)
        self.assertIn('&#91;fake&#93;',readme)
        self.assertIn('&amp; fix',readme)
        self.assertEqual(readme.count('](https://github.com/example/project/commit/123)'),1)
        self.assertNotIn('{{',readme)

    def test_empty_window_has_readable_zero_state(self):
        data=self.collect()
        self.assertEqual(data['total_commits'],0)
        self.assertIn('No project commits in this time window.',profile.render(data))
        self.assertTrue(all(p['commits_30d']==0 for p in data['projects']))
        self.assertIn('hourly sync',profile.render(data))

if __name__=='__main__':main()
