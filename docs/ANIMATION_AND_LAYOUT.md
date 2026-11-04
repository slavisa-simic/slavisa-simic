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

Each configured project has a real project capture, a short factual description, feature labels, and its technology stack. Desktop rows place the capture, description, and stack side by side; mobile artwork stacks them. The table uses GitHub's native row borders. Native Repository links sit beneath each row and open that project's repository root. The visually muted Demo artwork has no anchor and cannot navigate.

Vigil uses its actual sign-in screen. Potamorph uses the Industrial Port capture from its project README. Source images, SHA-256 hashes, and source URLs are in assets/profile/source/preview-provenance.json. No cloud deployments or features are claimed from the supplied visual reference.

Project artwork is self-contained SVG with embedded PNG captures. Repository buttons stay separate so they work as native keyboard-accessible links. The hourly workflow rebuilds these assets from bundled sources.
