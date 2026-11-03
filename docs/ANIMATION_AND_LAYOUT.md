# Native profile layout and motion

The page uses a compact editorial structure: identity and contacts, selected work, two repository links, skill tags, and one activity card. Project notes and raw commit messages remain available through disclosures. Native smaller headings and a shared graphite palette reduce competing visual elements.

## Identity

The supplied S logo retains its silver ribbon and fold shading. The Inter name and Plex role type once and settle by 2.7 seconds. Self-contained SVGs embed rasterized text, so no remote typing/font service is required. Light/dark and mobile variants have complete PNG identity fallbacks for reduced motion. If SVG animation is unsupported, the base clipping geometry exposes the complete text.

## Projects carousel

One centered image shows Vigil, slides horizontally to Potamorph, and loops. The whole carousel links to the visible `Projects list` heading below it. Each native list entry links directly to its project's `blob/main/README.md`, with no section fragment. There are no pretend previous/next buttons.

The desktop carousel is 1000 × 380 px; mobile uses a 480 × 450 composition. Each project is held for three seconds. A 400 ms eased translation produces a 6.8-second loop. Reduced motion uses instant project changes at three-second intervals with no moving transition, producing a six-second loop. Both variants repeat automatically.

Both supplied official logo PNGs remain byte-for-byte intact as source files. Rendering crops near-transparent outer padding, resizes proportionally, and composites the original pixels onto the new layout. Colors, shapes, lettering, and illustration detail are preserved. The Potamorph artwork is intentionally used as supplied, while surrounding typography and spacing stay restrained.

The self-contained SVG embeds lossless PNG slides. It needs no JavaScript, external images, or GIF palette reduction. A browser loads one approximately 369 KB desktop or 257 KB mobile variant. Native project links remain visible independently of animation. A static preview is available inside Project notes.

The reported non-advancing carousel was reproduced in the in-app browser: reduced motion was true and its selected image was `projects-carousel.png`. The revised picture source selects the non-sliding animated SVG in this mode. Verification must test the actual default preference as well as forced normal motion.

## Activity

The compact theme-aware card pairs commit/active-day counts with a thirty-day mini chart. Its source label and image description state the repository scope. Recent commit links are collapsed by default and the update date uses a short readable format. Counts describe repository commits, and the profile's own automation is excluded.

GitHub supports the native anchors, `picture`, `details`, and media queries used here. JavaScript is excluded from README content, so the carousel uses SVG motion with one stable external anchor. Body content stays native and keyboard accessible.
