"""Exercise avatar refresh, offline rebuilds, and preservation of the profile."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase,main
from unittest.mock import patch
import copy
import json
import sys
from base64 import b64encode
from hashlib import sha256

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import refresh_profile as profile
from tech_stack import header_base


class ProfileRefresh(TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.out=self.root/'profile';self.out.mkdir()
        self.config=copy.deepcopy(profile.CONFIG)
        self.avatar=self.make_avatar(b'original avatar')
        (self.out/'avatar.json').write_text(json.dumps(self.avatar),encoding='utf-8')
        for key,value in {'ROOT':self.root,'OUT':self.out,'MEDIA':self.out/'generated','CONFIG':self.config}.items():
            patcher=patch.object(profile,key,value);patcher.start();self.addCleanup(patcher.stop)
        (self.root/'src').mkdir()
        original=Path(__file__).resolve().parents[1]/'src/README.template.md'
        (self.root/'src/README.template.md').write_text(original.read_text(encoding='utf-8'),encoding='utf-8')
        (self.out/'generated').mkdir()
        source=Path(__file__).resolve().parents[1]/'assets/profile/generated'
        for asset in source.glob('tech-carousel*.svg'):
            (self.out/'generated'/asset.name).write_bytes(asset.read_bytes())

    def make_avatar(self,payload):
        return {'source':'https://avatars.githubusercontent.com/u/123?v=4&s=256','mime':'image/png',
                'sha256':sha256(payload).hexdigest(),'data_uri':'data:image/png;base64,'+b64encode(payload).decode()}

    def test_offline_rebuild_uses_only_cached_avatar_and_is_noop(self):
        with patch.object(profile,'api') as api,patch.object(profile.profile_avatar,'fetch') as download:
            profile.refresh(offline=True)
            before={p:p.stat().st_mtime_ns for p in self.root.rglob('*') if p.is_file()}
            self.assertFalse(profile.refresh(offline=True)['changed'])
        api.assert_not_called()
        download.assert_not_called()
        self.assertEqual(before,{p:p.stat().st_mtime_ns for p in before})
        self.assertFalse((self.out/'activity.json').exists())

    def test_api_failure_preserves_every_published_file(self):
        profile.refresh(offline=True)
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with patch.object(profile,'api',side_effect=OSError('API unavailable')),self.assertRaises(OSError):
            profile.refresh()
        self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_avatar_change_at_same_url_updates_frame_and_readme(self):
        profile.refresh(offline=True)
        old=list((self.out/'generated').glob('profile-avatar-*.svg'))[0]
        old_readme=(self.root/'README.md').read_text(encoding='utf-8')
        replacement=self.make_avatar(b'new avatar at unchanged GitHub URL')
        with patch.object(profile,'api',return_value={'avatar_url':replacement['source']}) as api,patch.object(profile.profile_avatar,'fetch',return_value=replacement):
            profile.refresh()
        api.assert_called_once_with('/users/'+self.config['owner'])
        self.assertFalse(old.exists())
        self.assertEqual(len(list((self.out/'generated').glob('profile-avatar-*.svg'))),1)
        self.assertNotEqual(old_readme,(self.root/'README.md').read_text(encoding='utf-8'))
        framed=profile.profile_avatar.frame(replacement,self.config['theme'])[1]
        header=(self.out/'generated'/(header_base(framed)+'.svg')).read_text(encoding='utf-8')
        self.assertIn(b64encode(framed.encode()).decode(),header)
        self.assertEqual(json.loads((self.out/'avatar.json').read_text())['sha256'],replacement['sha256'])
        self.assertFalse(profile.refresh(offline=True)['changed'])

    def test_avatar_failure_preserves_last_good_profile(self):
        profile.refresh(offline=True)
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with patch.object(profile,'api',return_value={'avatar_url':self.avatar['source']}),patch.object(profile.profile_avatar,'fetch',side_effect=OSError('Avatar unavailable')),self.assertRaises(OSError):
            profile.refresh()
        self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_project_showcase_renders_without_activity_snapshot(self):
        readme=profile.render()
        self.assertIn('<strong>Vigil</strong>',readme)
        self.assertIn('<!-- commit-activity:start -->',readme)
        self.assertNotIn('{{',readme)
        self.assertNotIn('hourly sync',readme)


if __name__=='__main__':main()
