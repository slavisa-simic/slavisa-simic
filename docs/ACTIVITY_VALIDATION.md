# Repository Districts validation

Checked locally on November 4, 2026. No changes were committed, pushed, or published. GitHub Actions has not been executed remotely.

## Live source

The production collector fetched the public `slavisa-simic/vigil` default branch (`main`) through the GitHub REST API. A separate read through the connected GitHub tool returned the same complete history: 22 commits, all linked to `slavisa-simic`. No additional page was needed for this repository; pagination and a pinned head are covered by unit tests.

Snapshot window: **2025-11-05 through 2026-11-04, inclusive, UTC**. Head SHA: `d53911015121bf59455ca638ba4bc268b3a35878`.

| Metric | Verified value |
| --- | --- |
| Matching commits | 22 |
| Active days | 11 |
| Most active month | October 2026, 20 commits |
| Last author date in period | 2026-10-25 |
| Greatest daily count | 4 commits |

The independently checked daily totals were September 29: 2; October 1: 2; October 4: 3; October 5: 2; October 6: 2; October 8: 2; October 19: 1; October 21: 2; October 22: 4; October 23: 1; October 25: 1. Other dates in the window have zero matching commits. The auditable records are in `assets/profile/activity/commits.json`; no random or simulated activity is used by the collector or renderer.

## Checks performed

- Python suite: identity and verified-email mappings, unrelated authors, bot authors and committers, automation markers, timezone boundaries, inclusive 365-day window, month ties, paginated and SHA-deduplicated traversal, pinned branch head, independent repository metrics, disabled slots, empty repositories, API/private-repository failures, deterministic offline rebuilds, snapshot integrity, exact tile count, and static fallback.
- GitHub Markdown rendering and the existing profile browser checks: nine viewport widths from 320 to 1440 px, both themes, image loading, responsive sources, existing links, project table, and original sections.
- Activity browser checks: 320, 390, 768, and 1100 px; no page overflow; correct phone/desktop image selection; static source under reduced motion; live SMIL inside an image; pixel-identical start/end of the nine-second loop; no clipped SVG geometry/text; 365 tiles whose total equals 22.
- Existing project and technology animation checks: passed, including actual README image playback.
- Two subsequent same-day activity rebuilds, one live and one offline, returned no changed files. The existing profile's offline refresh also returned unchanged, preserving the new section.
- `git diff --check`: passed. Local previews were visually inspected for the graphite grid, technical outlines, restrained cyan towers, empty slots, and secondary metrics.

The generated animated desktop/mobile SVGs are approximately 92 KB each. Static variants are bundled. The ignored local HTML and screenshots are in `assets/previews/activity/`; full README screenshots are in `assets/previews/profile/`. Remote rendering and scheduled workflow execution can only be checked after the owner approves publication.
