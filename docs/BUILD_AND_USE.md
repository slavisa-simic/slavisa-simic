# Build and update the GitHub profile

The README retains its graphite title strips, blue/red accents, square frames, project cards, and native activity table. The responsive header combines the unchanged framed avatar, name, Software Engineer title, and transparent technology marquee. GitHub Repositories and LinkedIn remain separate native links. Project notes and recent commits stay collapsed.

## Rebuild

Use Python 3.11+ and Node.js 20+. On Windows:

```powershell
py -m pip install -r requirements.txt
npm ci
npx playwright install chromium
py scripts/build.py --preview --package
```

The renderer can reuse an installed Playwright Chromium or `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH`. Both official project logos, the personal S mark, and fonts are bundled. No image-generation or animation-hosting service is required. The preview uses GitHub's Markdown API and current styles.

Add `--offline` to reuse cached activity and the avatar. Cached media generation works offline; a new icon URL is downloaded once. Browser preview still needs GitHub access. Builds do not publish.

## Add a technology

Edit `config/tech-stack.json`. This is the authoritative personal stack: Java, Spring Boot, PostgreSQL, Docker, Python, and Codex. REST APIs and Authentication are retained as unused `capabilities` metadata and are no longer displayed. Project languages are never imported as personal skills.

Add an entry to `technologies`, for example:

```json
{
  "id": "typescript",
  "name": "TypeScript",
  "category": "language",
  "icon_url": "https://raw.githubusercontent.com/devicons/devicon/54cfe13ac10eaa1ef817a343ab0a9437eb3c2e08/icons/typescript/typescript-original.svg"
}
```

Use a unique lowercase ID and a pinned official/Devicon/Simple Icons SVG URL. Optional `color` and `light_color` set monochrome logo fills. Set `category` to `ai_tool` for AI development tools; their extra caption is generated automatically. Then run:

```powershell
py scripts/build_tech_carousel.py
npm run preview
npm run verify:animation
```

The generator caches the icon, computes item widths from the longest label, duplicates the sequence to cover the viewport, and rebuilds the SVGs, composed headers, and README using the existing activity snapshot. No manual frame editing is needed. `duration_seconds` controls the complete cycle (default 30 seconds); increasing it slows the marquee. `--check-cache` forbids network access and verifies cached icon hashes. Adding technologies updates the reduced-motion grid automatically too.

The existing GitHub Action rebuilds the carousel when the configuration, generator, fonts, or icon sources change, as well as during the hourly refresh. It records any newly cached icon alongside the generated output. Local commands never commit or push.

The header uses responsive SVG image compositions because GitHub strips custom layout CSS. The exact existing framed avatar SVG is embedded as image data; it is neither redrawn nor cropped. Below 769 px the portrait, name, role, and marquee stack vertically. The name and role are image text with a complete accessible alt description; activity stays selectable native text. Contact links remain independent, keyboard-accessible anchors. Their transparent alignment spacer collapses on mobile. This avoids a visible layout table border and broken float wrapping.

The animated SVGs contain one linear SMIL translation and no JavaScript, external fonts, or external image requests. True alpha transparency and edge fades work over either GitHub theme. The header always selects the moving marquee, including when the system requests reduced motion, as explicitly requested. Static grid exports remain available as separate files; the README does not automatically select them. Local validation uses GitHub's Markdown API, current GitHub styles, and the actual README picture sources in all eight size/theme/motion combinations. No GIF fallback is needed for verified SVG image playback. `decoration_right_gutter` controls the extra desktop space placing the upper-right decoration farther outward.

For an activity-only refresh, no third-party Python packages are needed:

```powershell
py scripts/refresh_profile.py
```

## Edit

- `config/profile.json`: identity, reference palette, captions, official-logo hashes, README links, and project carousel timing.
- `config/tech-stack.json`: personal stack, capabilities, pinned icons, marquee dimensions and timing.
- `src/README.template.md`: native document structure.
- `scripts/build_profile_assets.py`: responsive title strips; `scripts/build_carousel.py`: project slides and motion.
- `scripts/build_tech_carousel.py`: cached official icons, transparent tech marquee, static grids, and link artwork; `scripts/tech_stack.py`: shared data and responsive header composition.
- `scripts/prepare_badges.py`: retained legacy badge cache; the standalone badge section is no longer displayed.
- `scripts/refresh_profile.py`: public data collection and native statistics/README generation; `scripts/profile_avatar.py`: avatar download and square framing.
- `.github/workflows/profile.yml`: hourly activity/avatar refresh and tests.

Personal skills are maintained explicitly. Project technologies never become personal skills automatically.

The carousel holds each project for three seconds. Normal motion uses a 400 ms slide; reduced motion uses a three-second content switch with no sliding. The former PNG source for reduced motion caused the reported frozen carousel and has been replaced. A static preview link remains inside Project notes. Browser checks cover both motion preferences.

## Automatic activity

The workflow runs hourly at minute 17 UTC, on relevant source changes, and on manual dispatch. It fetches stars and the last 30 calendar days of commits for the two public repositories. Counts are rendered as native table text with a visible last-successful-sync timestamp. The workflow status badge links directly to its runs. GitHub may delay scheduled jobs; the displayed timestamp always records an actual successful fetch.

The standard repository `GITHUB_TOKEN` is sufficient. The entire fetch completes before replacing valid content, so a failed request leaves the previous snapshot intact. Successful fetches update the sync timestamp even when counts stay the same. Offline rebuilds remain no-ops when the cached data and sources are unchanged. The profile repository and its automation commits are excluded from statistics.

The same workflow requests the current avatar URL and downloads it without sending API credentials to the image host. `assets/profile/avatar.json` caches the original image and checksum. A changed photo produces a new framed SVG filename; the README switches to it automatically. The old frame is retired after its replacement exists. Change the picture in GitHub settings; the README follows it on the next successful hourly run.

## Verification and exports

`assets/previews/profile/` contains local desktop/mobile/light screenshots and browser, animation, and media reports. These review artifacts are ignored by Git. `scripts/validate_layout.py` checks lossless embedded slide images, unchanged logo pixels, and source integrity. `tests/` covers activity boundaries, pagination, safe rendering, no-op updates, and failure preservation.

`dist/profile-ready.zip` contains the README and required images as a snapshot. `dist/profile-source.zip` adds the build and automatic-refresh sources. Preserve the `assets/profile/` paths.

The active profile is published in [slavisa-simic/slavisa-simic](https://github.com/slavisa-simic/slavisa-simic). Earlier blueprint assets and authoring files remain as historical design references; `scripts/build.py` uses the current pipeline exclusively.
