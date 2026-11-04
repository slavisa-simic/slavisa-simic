# Commit Activity validation

Verified locally on November 4, 2026 for the inclusive period 2025-11-05 through 2026-11-04 (UTC).

| Project | Color | Commits | Active days | Peak month | Last author date |
| --- | --- | --- | --- | --- | --- |
| Vigil | Blue | 22 | 11 | October 2026 (20) | 2026-10-25 |
| Potamorph | Red | 15 | 3 | October 2026 (12) | 2026-11-03 |

Separate GitHub API reads confirmed both complete histories: 22 and 15 commits, all linked to slavisa-simic. The auditable SHAs and daily counts are in assets/profile/activity/commits.json.

The shared card has exactly 365 date tiles and 37 matching commits. Project-colored segments add to each daily total without fabricated data. One configuration can render up to three projects on the same card.

Validation covers author identity, timezone boundaries, pagination, pinned heads, SHA deduplication, independent per-project totals, stacked heights, empty periods, API failures, deterministic rebuilds, and static SVG exports. Browser checks cover one shared card, matching title image, desktop/mobile selection, GIF playback in both motion settings, bounds, and the six-second SVG loop. The original profile sections and animations are preserved.

The GIF exports have 48 frames and loop every six seconds. Desktop is approximately 136 KB; mobile is approximately 71 KB. Both are checked for visible pixel changes. Local previews are in assets/previews/activity/ and the full README preview is in assets/previews/profile/.
