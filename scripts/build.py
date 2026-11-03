"""Rebuild the profile from source. Add --preview for actual GitHub render validation."""
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
    args=parser.parse_args()
    run(sys.executable,'scripts/build_assets.py')
    run('node','scripts/render_assets.mjs')
    run(sys.executable,'scripts/generate_animations.py')
    run(sys.executable,'scripts/build_readme.py')
    if args.preview: run('node','scripts/render_preview.mjs')
    run(sys.executable,'scripts/validate_layout.py')
    if args.package: run(sys.executable,'scripts/package_profile.py')
if __name__=='__main__': main()
