# Profile layout and motion

The README uses graphite surfaces, thin frames, muted blue/red accents, and the existing official artwork. Theme tokens live in config/profile.json.

## Identity

The original framed avatar sits beside three aligned lines: the name at weight 700, Software Engineer at 500, and Backend & full-stack development at 400. The last line has no vertical accent. The technology marquee stays below these lines.

Native GitHub Repositories and LinkedIn buttons align with that text column. At 960 px and below, the header stacks and the links follow the stacked text's left edge. This breakpoint prevents the desktop artwork from shrinking independently of the native links. The About Me strip retains the simple backend/full-stack introduction.

Headers use versioned filenames. Their alt text includes the complete identity and technology list. The cached original avatar is embedded unchanged. Light/dark variants preserve contrast and transparency.

## Carousels

The technology marquee keeps its continuous rightward 30-second loop in both system motion modes, following the user's preference. Optional static exports remain separate.

The project carousel retains the existing card styles and original logo composites. Projects are held for three seconds, with a 400 ms slide; reduced motion uses three-second switches. The footer shows only centered active-position indicators. Its link goes to the project table.

## Project table

The table below the carousel replaces Projects list, commit/star statistics, the sync timestamp, project notes, recent changes, and the workflow badge.

One native Projects heading groups both the carousel and the table. There is no separate All projects title. Each row has four columns: screenshot; native project heading, category, and description; technology badges and optional note; and vertically stacked Repository/Demo actions. Screenshot cells center their image horizontally and vertically. Project copy is selectable and uses GitHub's normal typography. Feature tags and colored left accents are removed. Repository links open the matching repository root; the visually muted Demo artwork has no anchor. The layout prioritizes desktop; narrow screens may scroll the table horizontally.

Vigil uses its actual sign-in screen. Potamorph uses the Industrial Port capture from its project README. Source images, SHA-256 hashes, and source URLs are in assets/profile/source/preview-provenance.json. No cloud deployments or features are claimed from the supplied visual reference.

Only the screenshots, cached technology badges, and action artwork are images. Project text is ordinary HTML in the README. Badge SVGs are cached from Shields.io and do not require a live badge-server request when viewing the profile. The hourly workflow regenerates thumbnails and verifies the badge cache; it cannot recreate the retired static project cards.
