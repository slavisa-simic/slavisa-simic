# Build and update the GitHub profile

The profile contains the responsive identity and technology marquee, native contact links, About Me strip, project carousel, project table, and Commit Activity activity section. [Commit Activity](COMMIT_ACTIVITY.md) documents its independent configuration, data scope, daily updates, and previews. Vigil (blue) and Potamorph (red) share one activity card.

## Rebuild

Use Python 3.11+ and Node.js 20+ with the pinned dependencies:

```powershell
py -m pip install -r requirements.txt
npm ci
npx playwright install chromium
py scripts/build.py --offline --preview --package
```

Remove --offline to fetch fresh commit activity and the current avatar. Offline builds reuse their cached snapshots. Commit Activity displays author-filtered commits over 365 days. Local commands do not commit or push.

Browser previews use GitHub's Markdown API and current GitHub styles. The renderer can reuse installed Playwright Chromium or PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH. Verification covers responsive layout, native links, inactive Demo placeholders, theme variants, and both carousels.

## Edit

- config/profile.json: identity, theme, projects, native descriptions, source captures, technology stacks, and carousel timing.
- config/tech-stack.json: the personal technology list, pinned vendor icon URLs, marquee dimensions, and timing. Project stacks remain separate from personal skills.
- config/activity.json: up to three projects on one shared timeline, period, timezone, author identity mappings, and automation exclusions.
- src/README.template.md: the visible README structure.
- scripts/tech_stack.py: responsive header, typography, contact alignment spacer, and About Me artwork.
- scripts/build_carousel.py: existing project card styles, animation, and centered indicators.
- scripts/build_project_table.py: screenshot thumbnails, repository button artwork, and inactive Demo artwork.
- scripts/prepare_badges.py: locally cached Shields.io technology badges and their source checksums.
- scripts/refresh_profile.py: native markup, real repository destinations, and avatar updates.
- scripts/build_activity.py: the independent commit collector and activity card exports.
- assets/profile/source/preview-provenance.json: original project-capture sources and checksums.

Run py scripts/build_tech_carousel.py after adding a technology. New pinned icon URLs are cached once; --check-cache verifies the cache offline. The existing hourly workflow rebuilds both project visuals and the marquee before refreshing the avatar. Adding a showcase row requires a bundled capture and a showcase object on the configured project.

## Layout constraints

The three identity lines use weights 700, 500, and 400. Contacts align with their left edge. Below 961 px the identity stacks before the desktop SVG would need scaling.

The Projects section retains its original title image, followed by the carousel and a native four-column table. Columns contain the centered screenshot; selectable project name, category, and description; technology badges and note; and vertically stacked Repository/Demo actions. All cells use native horizontal/vertical centering. Project names use bold paragraphs to avoid the extra top margin GitHub applies to headings inside table cells. The layout prioritizes desktop and permits horizontal table scrolling on narrow screens. There is no All projects heading, feature-tag row, or colored left accent. Repository links are separate native anchors; Demo images have no href. Captures are proportionally resized without manufacturing a new UI or gameplay scene.

The project carousel holds each card for three seconds and uses 400 ms slides. Reduced motion keeps three-second content switches. The technology marquee continues moving in both system motion modes, per the user's earlier preference. The carousel links to the stable projects-list anchor above the new table.

## Verification and exports

assets/previews/profile/ contains ignored desktop/mobile/light screenshots and browser, animation, and asset validation reports. dist/profile-ready.zip contains the README and required display assets; dist/profile-source.zip includes the reproducible source pipeline. Preserve the assets/profile paths.

`npm run preview:activity` separately verifies desktop/mobile activity images, animated GIF playback in both system motion settings, SVG bounds, data totals, and animation looping. Its local HTML, screenshots, and validation report are in `assets/previews/activity/`.

The published profile repository is https://github.com/slavisa-simic/slavisa-simic. Build commands only update the local checkout and export archives.

Both update workflows publish their committed snapshots through `scripts/push_snapshot.py`. GitHub's `remote: fatal error in commit_refs` response triggers at most two retries, after 5 and 15 seconds. Other push failures stop immediately; persistent failures still fail the job and retain the original Git diagnostics. Pushes use Git's normal fast-forward protection.

The Projects and GitHub Activity title images use a six-second light sweep along their technical divider; About Me uses a matching perimeter highlight. Text stays still. Animated SVG sources are selected in both system motion settings. Run `node scripts/verify_section_animation.mjs` after the profile preview to verify playback and seamless loops.
