# Terminal profile validation

Checked on 3 November 2026 for the native terminal redesign.

- Identity, role, contacts, shell headings, and statistics are native selectable text. The S mark is the only header image; the old image-based identity and activity chart are removed.
- Genuine Shields.io badges cover Java, Spring Boot, PostgreSQL, Docker, and OpenAI Codex. Codex is explicitly under AI Development Tools. Unity and C# appear only in project notes.
- Vigil uses its light blueprint identity. Potamorph has its own darker teal/rust identity, with its name, short description, and official logo. Both use the same fixed Explore projects footer.
- All four carousel variants hold each project for three seconds. Normal motion uses a 400 ms slide; reduced motion switches without sliding. Actual embedded playback and the exact loop clone pass.
- Logo source hashes and generated proportional composites match the supplied marks. No regenerated or recolored project logos are used.
- Nine viewport widths from 320 to 1440 px pass overflow, navigation, disclosure, badge loading, theme, and reduced-motion checks.
- Native table values match the API snapshot, including per-repository 30-day commit counts and stars. Successful-sync time is visible; the hourly GitHub workflow updates it even if counts stay unchanged.
- Seven updater tests cover pagination, date boundaries, private/profile repository exclusion, sync timestamps, offline no-op rebuilds, failure preservation, escaping, and the empty state.

Machine-readable browser, animation, source, and public-profile evidence is retained locally in assets/previews/profile.

The published terminal profile passed public browser checks at 1440, 390, and 320 px. The [hourly refresh workflow](https://github.com/slavisa-simic/slavisa-simic/actions/runs/41716266707) completed successfully and created its own [automated update commit](https://github.com/slavisa-simic/slavisa-simic/commit/da23b16), updating both README.md and activity.json. The successful API sync time advanced to 20:50:39 UTC on 3 November 2026. This verifies actual automatic writeback, not just an installed schedule.
