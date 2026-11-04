"""Regress the GitHub push failure without publishing to GitHub."""
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import call, patch
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import push_snapshot as publish

COMMIT_REFS = 'remote: fatal error in commit_refs\n ! [remote rejected] HEAD -> main (failure)\n'


class SnapshotPush(TestCase):
    def push(self, results):
        stdout, stderr = StringIO(), StringIO()
        with patch.object(publish.subprocess, 'run', side_effect=results) as run, \
                patch.object(publish.time, 'sleep') as sleep, \
                redirect_stdout(stdout), redirect_stderr(stderr):
            code = publish.push_snapshot()
        for invocation in run.call_args_list:
            self.assertEqual(invocation.args[0], ['git', 'push', 'origin', 'HEAD:main'])
        return code, run, sleep, stdout.getvalue(), stderr.getvalue()

    def result(self, code=0, stderr=''):
        return subprocess.CompletedProcess([], code, stdout='', stderr=stderr)

    def test_success_does_not_retry_or_sleep(self):
        code, run, sleep, _, _ = self.push([self.result()])
        self.assertEqual(code, 0)
        self.assertEqual(run.call_count, 1)
        sleep.assert_not_called()

    def test_commit_refs_failure_recovers_and_keeps_diagnostics(self):
        code, run, sleep, stdout, stderr = self.push([
            self.result(1, COMMIT_REFS), self.result(),
        ])
        self.assertEqual(code, 0)
        self.assertEqual(run.call_count, 2)
        sleep.assert_called_once_with(5)
        self.assertIn('attempt 2/3', stdout)
        self.assertIn(COMMIT_REFS, stderr)

    def test_persistent_commit_refs_error_fails_after_bounded_retries(self):
        code, run, sleep, stdout, _ = self.push([self.result(1, COMMIT_REFS)]*3)
        self.assertEqual(code, 1)
        self.assertEqual(run.call_count, 3)
        self.assertEqual(sleep.call_args_list, [call(5), call(15)])
        self.assertIn('::error::', stdout)

    def test_other_failures_stop_immediately(self):
        for error in (' ! [rejected] HEAD -> main (fetch first)',
                      'remote: Permission denied', 'fatal: Authentication failed'):
            with self.subTest(error=error):
                code, run, sleep, _, stderr = self.push([self.result(128, error)])
                self.assertEqual(code, 128)
                self.assertEqual(run.call_count, 1)
                sleep.assert_not_called()
                self.assertIn(error, stderr)

    def test_real_git_push_preserves_newer_remote_commits(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)

            def git(*args):
                return subprocess.run(['git', *args], cwd=root, check=True,
                                      capture_output=True, text=True).stdout.strip()

            git('init', '--bare', str(root/'remote.git'))
            git('init', '-b', 'main', str(root/'work'))
            root = root/'work'
            git('config', 'user.name', 'Snapshot Test')
            git('config', 'user.email', 'snapshot@example.test')
            git('remote', 'add', 'origin', str(root.parent/'remote.git'))
            git('commit', '--allow-empty', '-m', 'initial')
            command = [sys.executable, str(ROOT/'scripts/push_snapshot.py')]
            first = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            git('commit', '--allow-empty', '-m', 'newer remote commit')
            git('push', 'origin', 'HEAD:main')
            remote_head = git('rev-parse', 'HEAD')
            git('checkout', '--detach', 'HEAD~1')
            git('commit', '--allow-empty', '-m', 'stale snapshot')
            rejected = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertNotIn('retrying', rejected.stdout)
            self.assertEqual(git('--git-dir', str(root.parent/'remote.git'),
                                 'rev-parse', 'refs/heads/main'), remote_head)
