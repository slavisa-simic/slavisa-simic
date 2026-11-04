# Commit Activity

One card shows a shared 365-day timeline. Vigil is blue; Potamorph is red. The architecture accepts up to three repositories, with no placeholder for the unused third project.

## Update

```powershell
py scripts/build_activity.py
py scripts/build_activity.py --offline
py -m unittest discover -s tests
npm run preview:activity
```

Use Python 3.11+, Node.js 20+, the pinned Python/npm dependencies, and Playwright Chromium. On Linux replace `py` with `python3`. Local builds do not publish.

## Add a project

Append `{ "name": "Project", "repo": "owner/repo", "color": "#A9B4C7", "enabled": true }` to `config/activity.json`, then rebuild. Every enabled project appears on the same card, with its own color, metrics, and repository link. At most three entries are allowed. Disabled entries make no API requests.

`periodDays`, `timezone`, optional per-project `branch`, and `author` rules control collection. Username matching uses GitHub-linked accounts. `verifiedEmails` accepts owner-confirmed mappings only for otherwise unlinked commits. Bots and configured automation markers are excluded by default. A conflicting linked account overrides an email mapping.

## Data

Each tile is one calendar date; each colored segment contains that project's commits for that date. Segments stack additively. Height is linear in total commits per day and uses the same scale for every project. The 14-day strips read back to front, then continue right. Zero days are flat. No fabricated activity is used.

The API collector paginates the selected branch, pins the head SHA, deduplicates commits, and groups author timestamps in UTC by default. Merge commits count once. Co-author trailers and other branches are not added separately. The visible metrics are period commits, active days, peak month (ties indicated), and last author date within the displayed period. Today and boundary months may be partial. Repository commit totals differ from GitHub profile contributions.

`assets/profile/activity/commits.json` records the matching SHAs, author timestamps, daily counts, branch head, range, and calculated metrics. API errors fail the update and preserve published files. Offline mode validates the cached snapshot and retains its original range.

## Animation and daily automation

The README uses optimized desktop/mobile GIFs, rendered from the data-driven SVGs. The six-second loop has moving colored circuit lines and illuminated column tops; it never changes heights or counts. GIF playback remains enabled in both system motion settings, matching the requested visible animation. Static SVG exports remain available in `assets/profile/generated/`.

The title images use the exact generator and typography used by Projects. README copy is limited to the card and repository links.

`.github/workflows/activity.yml` updates daily at 05:43 UTC and supports manual dispatch. It installs the renderer dependencies, fetches real data, regenerates changed assets, and commits only the activity files and README. Source hashes avoid re-encoding unchanged GIFs. The default GitHub Actions token is sufficient for these public repositories. Both profile workflows share a concurrency group to serialize README updates.

Local previews and validation reports are in `assets/previews/activity/` (ignored by Git). Open `index.html` or inspect the full GitHub-sanitized profile preview using `npm run preview`.
