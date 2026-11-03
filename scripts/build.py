"""Rebuild the native profile and its compact media. Does not publish."""
from pathlib import Path
import argparse
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
def run(*args): subprocess.run(args,cwd=ROOT,check=True)
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview',action='store_true')
    parser.add_argument('--package',action='store_true')
    parser.add_argument('--offline',action='store_true',help='Reuse the last valid activity snapshot')
    args=parser.parse_args()
    run(sys.executable,'scripts/prepare_profile_sources.py')
    run(sys.executable,'scripts/prepare_badges.py')
    run(sys.executable,'scripts/build_profile_assets.py')
    run(sys.executable,'scripts/refresh_profile.py',*(['--offline'] if args.offline else []))
    run(sys.executable,'-m','unittest','discover','-s','tests')
    if args.preview:
        run('node','scripts/preview_profile.mjs')
        run('node','scripts/verify_profile_animation.mjs')
    run(sys.executable,'scripts/validate_layout.py')
    if args.package: run(sys.executable,'scripts/package_profile.py')
if __name__=='__main__': main()
