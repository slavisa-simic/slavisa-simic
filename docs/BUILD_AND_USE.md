# Build and update the GitHub profile

The profile contains the responsive identity and technology marquee, native contact links, About Me strip, project carousel, and a project table. It ends after the project rows; activity counts, recent changes, notes, and the workflow badge are currently hidden.

## Rebuild

Use Python 3.11+ and Node.js 20+ with the pinned dependencies:

```powershell
py -m pip install -r requirements.txt
npm ci
npx playwright install chromium
py scripts/build.py --offline --preview --package
```

Remove --offline to fetch fresh activity and the current avatar. Offline builds reuse their cached snapshots. The activity collector remains available for future use, but its results are not displayed. Local commands do not commit or push.

Browser previews use GitHub's Markdown API and current GitHub styles. The renderer can reuse installed Playwright Chromium or PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH. Verification covers responsive layout, native links, inactive Demo placeholders, theme variants, and both carousels.

## Edit

- config/profile.json: identity, theme, projects, native descriptions, source captures, technology stacks, and carousel timing.
- config/tech-stack.json: the personal technology list, pinned vendor icon URLs, marquee dimensions, and timing. Project stacks remain separate from personal skills.
- src/README.template.md: the visible README structure.
- scripts/tech_stack.py: responsive header, typography, contact alignment spacer, and About Me artwork.
- scripts/build_carousel.py: existing project card styles, animation, and centered indicators.
- scripts/build_project_table.py: screenshot thumbnails, repository button artwork, inactive Demo artwork, and retirement of old static cards.
- scripts/prepare_badges.py: locally cached Shields.io technology badges and their source checksums.
- scripts/refresh_profile.py: native markup, real repository destinations, avatar updates, and the retained activity collector.
- assets/profile/source/preview-provenance.json: original project-capture sources and checksums.

Run py scripts/build_tech_carousel.py after adding a technology. New pinned icon URLs are cached once; --check-cache verifies the cache offline. The existing hourly workflow rebuilds both project visuals and the marquee before refreshing the avatar. Adding a showcase row requires a bundled capture and a showcase object on the configured project.

## Layout constraints

The three identity lines use weights 700, 500, and 400. Contacts align with their left edge. Below 961 px the identity stacks before the desktop SVG would need scaling.

The Projects section retains its original title image, followed by the carousel and a native four-column table. Columns contain the centered screenshot; selectable heading, category, and description; technology badges and note; and vertically stacked Repository/Demo actions. Screenshot cells use native horizontal/vertical centering. The layout prioritizes desktop and permits horizontal table scrolling on narrow screens. There is no All projects heading, feature-tag row, or colored left accent. Repository links are separate native anchors; Demo images have no href. Captures are proportionally resized without manufacturing a new UI or gameplay scene.

The project carousel holds each card for three seconds and uses 400 ms slides. Reduced motion keeps three-second content switches. The technology marquee continues moving in both system motion modes, per the user's earlier preference. The carousel links to the stable projects-list anchor above the new table.

## Verification and exports

assets/previews/profile/ contains ignored desktop/mobile/light screenshots and browser, animation, and asset validation reports. dist/profile-ready.zip contains the README and required display assets; dist/profile-source.zip includes the reproducible source pipeline. Preserve the assets/profile paths.

The published profile repository is https://github.com/slavisa-simic/slavisa-simic. Build commands only update the local checkout and export archives.
