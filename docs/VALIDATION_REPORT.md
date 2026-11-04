# Profile layout validation

Validated locally with GitHub-rendered Markdown and current GitHub styles. The activity and avatar snapshots were reused. These changes are local.

- Project names, categories, descriptions, the Tech stack label, and the Codex note are native HTML text. Browser selection retrieves each complete project description at all tested widths.
- The original Projects title image contains the carousel and four-column table: screenshot, description, technology badges, and vertically stacked actions. Desktop browser measurements confirm each screenshot is centered horizontally and vertically within one pixel. The All projects heading, feature tags, colored left accents, and flattened project-card SVGs are removed.
- Each project has its real screenshot and cached technology badges. Vigil has Java, Spring Boot, React, TypeScript, PostgreSQL, and Docker. Potamorph has Unity, C#, and UI Toolkit.
- Nine widths pass without page overflow: 320, 375, 390, 600, 601, 768, 844, 1024, and 1440 px. The table fills the content width and has no internal overflow at desktop widths of 1024 and 1440 px. Narrow screens may scroll the four-column table horizontally, as accepted by the user. Native text remains selectable; light/dark modes and enlarged native text pass.
- Repository links open the correct repository roots with both pointer and keyboard input. Demo placeholders remain unlinked. Header contacts still align with the identity text column.
- Fifteen unit tests pass. Asset validation checks original logo composites, avatar bytes, screenshot source hashes, badges, embedded resources, and media budgets.
- All four project carousel variants retain their three-second holds, transitions, loop, actual image playback, and synchronized centered indicators. The technology marquee passes speed, seamless loops, transparency, and actual README image playback in all eight size/theme/system-motion combinations.
- The workflow caches badges and regenerates screenshots without recreating static text cards. Git diff whitespace checks pass.

Review screenshots and reports are under assets/previews/profile/ (ignored by Git): desktop.png, mobile.png, light.png, browser-report.json, animation-report.json, tech-animation-report.json, and validation-report.json. Original project capture provenance is under assets/profile/source/; badge provenance is under assets/profile/badges/.
