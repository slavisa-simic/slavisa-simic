# Build and update the GitHub profile

The README uses a terminal theme with a native selectable identity, the preserved S logo, distinct project carousel cards, Shields.io stack badges, and a native API-generated statistics table. Project notes and recent commits are collapsed. Potamorph showcases AI-assisted development; Unity/C# remain project details rather than personal skills.

## Rebuild

Use Python 3.11+ and Node.js 20+. On Windows:

```powershell
py -m pip install -r requirements.txt
npm ci
npx playwright install chromium
py scripts/build.py --preview --package
```

The renderer can reuse an installed Playwright Chromium or `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH`. Both official project logos, the personal S mark, and fonts are bundled. No image-generation or animation-hosting service is required. The preview uses GitHub's Markdown API and current styles.

Add `--offline` to reuse the cached activity snapshot. Media generation works offline; browser preview still needs GitHub access. Builds do not publish.

For an activity-only refresh, no third-party Python packages are needed:

```powershell
py scripts/refresh_profile.py
```

## Edit

- `config/profile.json`: identity, skills, project captions, official-logo hashes, README links, and carousel timing.
- `src/README.template.md`: native document structure.
- `scripts/build_profile_assets.py`: preserved logo; `scripts/build_carousel.py`: project slides and horizontal motion.
- `scripts/prepare_badges.py`: cache genuine Shields.io badges locally, recording URLs and hashes.
- `scripts/refresh_profile.py`: public data collection and native statistics/README generation.
- `.github/workflows/profile.yml`: scheduled activity refresh and tests.

Personal skills are maintained explicitly. Project technologies never become personal skills automatically.

The carousel holds each project for three seconds. Normal motion uses a 400 ms slide; reduced motion uses a three-second content switch with no sliding. The former PNG source for reduced motion caused the reported frozen carousel and has been replaced. A static preview link remains inside Project notes. Browser checks cover both motion preferences.

## Automatic activity

The workflow runs hourly at minute 17 UTC, on relevant source changes, and on manual dispatch. It fetches stars and the last 30 calendar days of commits for the two public repositories. Counts are rendered as native table text with a visible last-successful-sync timestamp. The workflow status badge links directly to its runs. GitHub may delay scheduled jobs; the displayed timestamp always records an actual successful fetch.

The standard repository `GITHUB_TOKEN` is sufficient. The entire fetch completes before replacing valid content, so a failed request leaves the previous snapshot intact. Successful fetches update the sync timestamp even when counts stay the same. Offline rebuilds remain no-ops when the cached data and sources are unchanged. The profile repository and its automation commits are excluded from statistics.

## Verification and exports

`assets/previews/profile/` contains local desktop/mobile/light screenshots and browser, animation, and media reports. These review artifacts are ignored by Git. `scripts/validate_layout.py` checks lossless embedded slide images, unchanged logo pixels, and source integrity. `tests/` covers activity boundaries, pagination, safe rendering, no-op updates, and failure preservation.

`dist/profile-ready.zip` contains the README and required images as a snapshot. `dist/profile-source.zip` adds the build and automatic-refresh sources. Preserve the `assets/profile/` paths.

The active profile is published in [slavisa-simic/slavisa-simic](https://github.com/slavisa-simic/slavisa-simic). Earlier blueprint assets and authoring files remain as historical design references; `scripts/build.py` uses the current pipeline exclusively.
