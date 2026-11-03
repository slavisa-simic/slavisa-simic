# Build and update the GitHub profile

The root README uses native GitHub content with a typed identity, one centered projects carousel, a linked project list, expandable details, a short toolkit, and real repository activity. Potamorph showcases AI-assisted development; Unity and C# describe its implementation and are not personal skills.

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
- `scripts/build_profile_assets.py`: typing identity; `scripts/build_carousel.py`: project slides and horizontal motion.
- `scripts/refresh_profile.py`: public data collection, chart, and README generation.
- `.github/workflows/profile.yml`: scheduled activity refresh and tests.

Personal skills are maintained explicitly. Project technologies never become personal skills automatically.

## Automatic activity

The workflow runs on a six-hour schedule, relevant source changes, and manual dispatch. It fetches the two public repositories, updates the last 30 calendar days of repository commits, and writes only changed activity files. This is a scheduled snapshot, not a streaming service. GitHub may delay scheduled runs.

The standard repository `GITHUB_TOKEN` is sufficient. No personal access token or external statistics service is required. The entire fetch and rendering completes before replacing valid content. A failed fetch leaves the previous snapshot intact; unchanged data preserves its timestamp and creates no bot commit. The profile repository is explicitly excluded from the activity scope.

## Verification and exports

`assets/previews/profile/` contains local desktop/mobile/light screenshots and browser, animation, and media reports. These review artifacts are ignored by Git. `scripts/validate_layout.py` checks lossless embedded slide images, unchanged logo pixels, and source integrity. `tests/` covers activity boundaries, pagination, safe rendering, no-op updates, and failure preservation.

`dist/profile-ready.zip` contains the README and required images as a snapshot. `dist/profile-source.zip` adds the build and automatic-refresh sources. Preserve the `assets/profile/` paths.

The active profile is published in [slavisa-simic/slavisa-simic](https://github.com/slavisa-simic/slavisa-simic). Earlier blueprint assets and authoring files remain as historical design references; `scripts/build.py` uses the current pipeline exclusively.
