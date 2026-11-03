# Profile validation

Checked on 3 November 2026 for the native profile redesign.

- GitHub's Markdown API preserves the required anchors, picture sources, details, and media conditions.
- Browser checks cover 320, 375, 390, 600, 601, 768, 844, 1024, and 1440 px, including landscape. No document or table horizontal overflow occurs.
- The single carousel and both native project destinations pass pointer and keyboard activation. The carousel targets the visible Projects list; each project link opens its README from the top. The carousel click target exceeds 44 × 44 px.
- Light/dark rendering, enlarged native text, native disclosures, mobile sources, and reduced-motion PNG selection pass.
- Chromium checks the actual typing timeline in all four SVG variants. The name progresses, all lines finish, cursors disappear, and the result remains complete. The SVG also animates when embedded as an image.
- Both carousel variants hold each project for five seconds, slide horizontally over 600 ms, and loop after 11.2 seconds. Actual Chromium playback passes both as an SVG document and embedded image. The first-slide PNG fallback, media budget, and exact first-slide loop clone pass validation.
- Each embedded logo region matches the original proportional source composite pixel-for-pixel. Source files match the SHA-256 hashes of the supplied PNGs; no palette quantization, recoloring, or regenerated artwork is used.
- Original project sources match their provenance hashes; all README images are local to the repository. SVGs have no scripts or external image dependencies.
- Seven updater tests cover paginated data and date boundaries, exclusion of profile automation/private repositories, no-op writes, API failure preservation, commit-text escaping, and the empty state.
- Personal skills exclude Unity and C#. OpenAI Codex appears under AI Development Tools; Potamorph's hidden detail distinguishes direction/scope from AI implementation.

Machine-readable reports and screenshots are regenerated under `assets/previews/profile/`. Previous blueprint validation concerns the earlier design only.

## Public verification

The redesign is published on the [actual profile](https://github.com/slavisa-simic). An unauthenticated browser checked its real images and markup at 1440, 390, and 320 px, including mobile sources, both themes, reduced motion, native details, and exact project README destinations. No markup or network responses were substituted during this check.

The first [activity workflow run](https://github.com/slavisa-simic/slavisa-simic/actions/runs/41700879653) completed successfully on 3 November 2026. Its checkout, Python setup, seven tests, public API fetch, and conditional commit step all passed. The six-hour schedule is installed. Public-browser evidence and the workflow result are retained locally in `assets/previews/profile/published-report.json` and `workflow-report.json`.

The official-logo carousel revision passed the public check at all three widths. Actual captures show both project slides in the same image element, and clicking that image scrolls to the visible Projects list. Its [activity refresh run](https://github.com/slavisa-simic/slavisa-simic/actions/runs/41706296646) also completed successfully. Original supplied-logo hashes and proportional composites pass the source/pixel checks.
