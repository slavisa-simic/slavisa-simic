# Repository Districts

The **GitHub Activity** section follows the project table. Its SVGs show **Repository Commit Activity**, derived from public GitHub REST commit records. These totals are not GitHub profile contribution counts. Only `slavisa-simic/vigil` is initially enabled. The other two slots show no activity or metrics.

## Build locally

Python 3.11+ is sufficient for the collector and SVG generator; they use the standard library. On Windows use `py`; on Linux/macOS use `python3`.

```powershell
py scripts/build_activity.py
py scripts/build_activity.py --offline
py -m unittest discover -s tests -p test_activity.py
npm ci
npx playwright install chromium
npm run preview:activity
```

The first command fetches actual data. `--offline` re-renders the stored snapshot without network requests. It rejects a snapshot whose configuration or calculated metrics no longer match. It keeps the snapshot's visible date range, rather than relabeling old data as current. Local commands never commit or push.

The preview command writes `assets/previews/activity/index.html`, desktop/mobile PNGs, and `validation.json`. Open the HTML file locally, or serve the repository root with `py -m http.server 8000` and open `http://localhost:8000/assets/previews/activity/`. `npm run preview` also renders the entire README using GitHub's Markdown API and styles. Previews are ignored by Git.

Set `GITHUB_TOKEN` or `GH_TOKEN` in the environment if authentication is needed. Never add a token to configuration. Public repositories also work without authentication, subject to GitHub rate limits. Non-UTC timezones require an IANA timezone database; on Windows, install `tzdata` if the selected zone is unavailable.

## Connect a second or third repository

Edit `config/activity.json` and append an entry to `repositories`:

```json
{
  "name": "Your next project",
  "repo": "your-account/your-repository",
  "color": "#A9B4C7",
  "enabled": true
}
```

Run `py scripts/build_activity.py`. No rendering code changes are needed. Each entry receives an independent card, API collection, statistics, configured accent, and native Markdown/HTML image link to its repository. The first three array positions are stable district slots. Setting `enabled` to `false` leaves that slot unconfigured and makes no API request for it. More than three entries are rejected. `maxProjects` stays at `3`.

`periodDays` defaults to `365` calendar dates, inclusive of today. `timezone` defaults to `UTC`. An optional per-repository `branch` selects a branch; otherwise the API's default branch is used. All cards in a generation use the same projection, spacing, linear height scale, and lighting. Adding a repository adds its own full-width card and retires its empty slot. Disabled or removed projects' generated SVGs are retired.

## Author identification and automation

The initial author rule accepts GitHub-linked `slavisa-simic` commits. Display names are never used to establish ownership. Matching is case-insensitive.

- `author.logins`: accepted GitHub account logins.
- `author.verifiedEmails`: explicit owner-confirmed email mappings for commits that GitHub cannot link to an account. Add an address only after confirming it belongs to your GitHub identity. A conflicting linked account is rejected even if its email matches. Addresses are not inferred from names and are not written into the generated snapshot.
- `author.includeBots`: defaults to `false`; rejects bot authors, bot committers, `[bot]` emails, and messages matching the configured automation patterns. Setting this to `true` still requires a matching author identity and still respects explicit exclusions.
- `author.excludedLogins` / `excludedEmails`: always-rejected author identities.
- `author.excludedMessagePatterns`: Python regular expressions identifying additional automated work. These apply when `includeBots` is false. Add a project-specific pattern if automation runs under a human account without a bot identity. Such automation cannot otherwise be distinguished reliably from human-authored commits.

An email mapping is an explicit identity assertion, separate from cryptographic commit signature verification. Unsigned commits linked by GitHub to the configured account still count.

## Data and statistical definitions

The collector enumerates every page (`per_page=100`) of commits reachable from the selected branch. The first page's head SHA pins subsequent pages so new pushes cannot shift pagination. It deduplicates SHAs, matches the author, and groups `commit.author.date` into the configured timezone. It deliberately does not use API `since`/`until` filters: update/committer dates can differ from author dates, especially after rebases. Large histories require more API requests; an API failure fails the update and preserves the existing published snapshot rather than producing zero or simulated data.

The period includes the start and end date, with today's activity still partial. Merge commits count once, as distinct SHAs. Other branches and co-author trailers are not counted separately. Private repositories are rejected. Empty repositories and periods with no matching commits produce zero totals and flat tiles.

- **Commits:** number of unique matching SHAs with author dates inside the range.
- **Active days:** dates containing at least one matching commit.
- **Most active month:** calendar month with the most matching commits in the range. Boundary months may be partial. Ties are stored in full; the card shows the earliest tied month and the number of additional ties. No active month is shown as a dash.
- **Last commit:** latest author date among matching commits within the displayed range; a dash means none.

The auditable snapshot, `assets/profile/activity/commits.json`, records daily counts, matching SHAs and author timestamps, the branch head, date boundaries, and calculated statistics. It contains no credentials, emails, commit messages, or fabricated records. The collector only uses repositories enabled in the separate activity configuration; the older hidden 30-day profile snapshot is not an input to these visualizations.

## Image compatibility and performance

Each tile represents exactly one date. Read 14 days down a strip (back to front), then continue to the next strip on the right. Date guides mark strip starts. The final strip contains only the remaining actual dates. Zero-activity tiles are flat. Height is strictly linear in daily commits, normalized against the greatest daily count across all connected projects; the legend states that scale. No decorative activity or height changes are introduced. Circuit traces are separate from the data footprint.

Desktop and phone SVGs have independent typography/layout. The initial animated assets are approximately 92 KB each. A restrained nine-second circuit/peak illumination loop uses SVG SMIL; the data geometry remains still. There is no JavaScript, external font, embedded remote image, HTML canvas, or dependency on CSS animation. Static SVG variants are selected for reduced motion. Viewers without SMIL support retain the complete, accurate static geometry. No GIF fallback is necessary for data visibility. Each image is wrapped in a native repository anchor because links inside README SVG images are not interactive.

## Daily automation

`.github/workflows/activity.yml` runs daily at **05:43 UTC**, supports `workflow_dispatch`, and rebuilds after activity configuration/source changes on `main`. It uses the default Actions token, runs the collector tests, generates and validates the assets, and stages only the activity snapshot, activity SVGs, and README integration. An unchanged staged diff exits without a commit. Identical same-day data produces identical bytes; advancing the calendar range legitimately changes the image even on days without commits.

The workflow shares a concurrency group with the existing hourly avatar/profile job to serialize README writes. The existing profile renderer knows about the activity section, so hourly rebuilds preserve it. The activity job has no Pillow or Node dependency. A protected branch may require the repository owner's normal workflow permission setup. The workflow becomes active only after these local changes are reviewed and explicitly published by the owner.

API contracts: [GitHub list commits](https://docs.github.com/en/rest/commits/commits#list-commits), [Actions token authentication](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token).
