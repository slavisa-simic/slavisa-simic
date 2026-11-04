"""Publish the committed snapshot, retrying GitHub's commit_refs error."""
import subprocess
import sys
import time


def push_snapshot():
    for attempt, delay in enumerate((0, 5, 15), start=1):
        if delay:
            print(f'::warning::GitHub commit_refs error; retrying push in {delay}s '
                  f'(attempt {attempt}/3).', flush=True)
            time.sleep(delay)
        result = subprocess.run(
            ['git', 'push', 'origin', 'HEAD:main'],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
        )
        print(result.stdout, end='', flush=True)
        print(result.stderr, end='', file=sys.stderr, flush=True)
        if result.returncode == 0:
            return 0
        if 'remote: fatal error in commit_refs' not in result.stderr:
            return result.returncode
    print('::error::GitHub still rejects the snapshot after 3 push attempts.', flush=True)
    return result.returncode


if __name__ == '__main__':
    sys.exit(push_snapshot())
