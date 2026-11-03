# Engineering Blueprint: layout and animation

The final visual follows the selected Engineering Blueprint mockup: graphite paper, Inter typography, restrained Plex labels, thin geometry, a monochrome System Core, and muted project colors. The supplied S mark is preserved. The former armored core and hexagonal project artwork remain reference files and are not used in the final profile.

## GitHub-compatible construction

The hero is one ordinary HTML paragraph containing five image rows. Standard image links provide seven click targets: brand, GitHub, LinkedIn, Vigil, System Core, Potamorph, and the repository footer.

1. Three linked masthead crops, at 70%, 15%, and 15% width.
2. One identity image, retaining the selected typography.
3. Three independently linked network panels, partitioned at 38.57143% and 61.42857% of the image width.
4. One combined legend and skills image.
5. One linked footer image.

All images use the supported `align="top"` attribute. Explicit `<br>` separators create rows, and adjacent anchors contain no whitespace. This avoids table borders and padding without relying on a custom stylesheet. The short legend is joined to the skills image because a separate narrow legend image can fall below GitHub's 24 px line box and introduce a gap.

The GitHub API preserved `align`, image widths, anchors, picture sources, and media conditions. The result was also measured inside a live GitHub repository page using its actual CSS and custom elements. No content was uploaded or saved to that repository.

The custom CSS and JavaScript in `src/` are **asset-authoring tools only**. GitHub receives PNGs, GIFs, and ordinary README markup. Embedded SVG click targets are not used.

## Coordinates and connectors

Coordinates in `config/network.json` are diagram-local CSS pixels. The desktop authoring canvas is 1120 px wide, with a 1024 × 430 diagram inset by 48 px. The mobile canvas is 390 px wide, with a 342 × 245 diagram inset by 24 px.

| Variant | Core west | Vigil input | Core east | Potamorph input |
| --- | --- | --- | --- | --- |
| Desktop | 430, 198 | 346, 216 | 594, 198 | 678, 216 |
| Mobile | 136, 122 | 112, 132 | 206, 122 | 230, 132 |

Every route starts at a defined core port and ends at a defined project input. Bends use horizontal, vertical, or exact 45° segments. The renderer draws paths from these points; validation rejects mismatched endpoints or arbitrary angles. The small project input rectangle and the fine core outline replace the old mechanical sockets.

Add the canvas padding to local X coordinates before scaling to output pixels. Each network is normalized to a 1120 px-wide master. Animation coordinates use the same transform. Panel edges are integer pixel cuts at X=432 and X=688.

## Motion

The 10.4-second loop uses 130 samples with exact 80 ms delays (12.5 fps). A single film is generated before cropping linked panels; each variant uses one shared GIF palette.

| Time | Behavior |
| --- | --- |
| 0–0.8 s | Complete, recognizable logo held at rest |
| 0.8–1.44 s | Logo settles into a faint guide |
| 1.44–3.04 s | Progressive reveal and a light trace clipped to the actual S pixels |
| 3.36–4.88 s | Small muted signals travel toward each project |
| 4.88–5.68 s | Project input and short top accent respond gently |
| 7.2–8.72 s | A second quiet transmission |
| 8.72–9.52 s | Project response, followed by the resting state |

The final frame and first frame are visually identical. There is no full-field flashing, fabricated telemetry, or animated armor. Signal activity represents the portfolio relationship, not a claim that two deployed products exchange data.

## Synchronization and fallbacks

Browsers can start separate GIF resources at different times. Shared generation does not guarantee synchronized playback on GitHub. Pulses fade near panel boundaries, and the outer three pixels on both sides of every cut remain invariant across every frame. Stationary connections therefore remain continuous during playback drift.

The complete `desktop/network.gif` and `mobile/network.gif` provide synchronized single-image reference views. The primary profile uses the linked crops. Validation decodes every timeline sample and checks that reassembled panels match their master exactly.

`<picture>` selects a dedicated mobile composition at viewport widths up to 600 px. Combined mobile and reduced-motion conditions select mobile PNGs; reduced motion on wider screens selects desktop PNGs. Standard browser behavior does not automatically substitute a PNG after a GIF network error. The README's static-view disclosure and native project descriptions remain available independently.

Hero typography is rasterized to preserve the approved appearance in both GitHub themes. The hero is not selectable text. Descriptive alt text, native project summaries, personal skills, AI-tool disclosure, and normal navigation supply readable and accessible content outside the images.

## Adding a project

The current layout deliberately gives two projects substantial space. Adding another project requires a layout decision, not a new asset pipeline:

1. Add a project object under `projects` in the JSON, including its name, category, summary, actual project technologies, URL, and separate desktop/mobile geometry.
2. Define its core port and an orthogonal/45° route. Keep route endpoints outside unrelated modules.
3. Add a linked `panels` region and alt text. Panel intervals must partition 0–1 without gaps, with each clickable module wholly inside its own region. Keep the core in its own region.
4. Adjust canvas width, diagram dimensions, core placement, and all affected boxes if more room is needed. The canvas width and padding are configurable; all project modules and signals render from the project array.
5. Add the native project summary to `src/README.template.md`. Personal skills must remain a separately maintained list.
6. Run the full build and inspect both previews. The validator checks route math, panel coverage, decoded seams, timing, file budgets, image paths, and links. The browser checks derive their network panel count from the configuration.

For a large project collection, use multiple clearly separated architecture views rather than making every module too small. The existing two-project composition should not be crowded merely to avoid adjusting the layout.
