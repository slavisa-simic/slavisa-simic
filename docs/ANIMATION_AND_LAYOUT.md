# Native profile layout and motion

The page contains one introduction, one caption per project, one toolkit, and one recent-work section. GitHub renders all body text, links, and expandable details natively. Custom CSS and JavaScript are used only for local authoring/verification.

## Identity

The supplied S logo retains its silver ribbon and fold shading. The name and role type once and settle by 4.2 seconds. Self-contained SVGs embed rasterized Inter text, so no remote typing/font service is required. Light/dark and mobile variants have complete PNG fallbacks for reduced motion. If SVG animation is unsupported, the base clipping geometry exposes the complete text.

## Projects carousel

One centered image shows Vigil, slides horizontally to Potamorph, and loops. The whole carousel links to the visible `Projects list` heading below it. Each native list entry links directly to its project's `blob/main/README.md`, with no section fragment. There are no pretend previous/next buttons.

The desktop carousel is 1000 × 420 px; mobile uses a 480 × 480 composition with larger relative typography and a centered logo. Each project is held for five seconds. A 600 ms eased translation creates the classic sliding-carousel effect. The complete two-project loop lasts 11.2 seconds, using an exact duplicate of the first slide for the loop boundary.

Both supplied official logo PNGs remain byte-for-byte intact as source files. Rendering crops near-transparent outer padding, resizes proportionally, and composites the original pixels onto the new layout. Colors, shapes, lettering, and illustration detail are preserved. The Potamorph artwork is intentionally used as supplied, while surrounding typography and spacing stay restrained.

The self-contained SVG embeds lossless PNG slides and animates their translation. It needs no JavaScript, external images, or GIF palette reduction. The desktop animation is approximately 497 KB and mobile approximately 308 KB; only the selected variant loads. Reduced motion selects a complete first-slide PNG. Native project links remain visible independently of the animation.

## Activity

The chart is a static, theme-aware SVG generated from current public repository commits. Its title, native recent-commit links, and snapshot label describe the scope. Counts include repository commits rather than claiming personal contributions or expertise. The profile's own automation commits are excluded.

GitHub supports the native anchors, `picture`, `details`, and media queries used here. JavaScript is excluded from README content, so the carousel uses SVG motion with one stable external anchor. Body content stays native and keyboard accessible.
