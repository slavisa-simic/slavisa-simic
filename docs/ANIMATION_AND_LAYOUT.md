# Native profile layout and motion

The page contains one introduction, one caption per project, one toolkit, and one recent-work section. GitHub renders all body text, links, and expandable details natively. Custom CSS and JavaScript are used only for local authoring/verification.

## Identity

The supplied S logo retains its silver ribbon and fold shading. The name and role type once and settle by 4.2 seconds. Self-contained SVGs embed rasterized Inter text, so no remote typing/font service is required. Light/dark and mobile variants have complete PNG fallbacks for reduced motion. If SVG animation is unsupported, the base clipping geometry exposes the complete text.

## Project slideshows

Each project owns one anchor whose destination is always that project's `blob/main/README.md`, with no section fragment. A single GIF cannot switch its external link when its frame changes. Two separate slideshow previews make every displayed frame open the appropriate README from the beginning.

Desktop previews are 900 × 500 px. Each cycles through original header artwork, an actual application screenshot, and a small architecture/workflow view. Holds last five seconds; crossfades take 280 ms. The 15.84-second loop uses 24 decoded frames per image. The project name remains visible in every frame.

Mobile previews are 360 × 320 px with larger names and two artwork/screenshot frames. Their 10.56-second loops contain 16 frames. Two-column native GitHub tables keep both projects accessible without a horizontal scrollbar. Native captions and details provide readable context independently of the thumbnails.

Browsers download only the selected desktop/mobile media. The desktop GIF pair totals 1,899,246 bytes; the mobile pair totals 615,463 bytes. Reduced motion selects complete first-frame PNGs. Static fallbacks are preference-based; they are not automatic recovery from failed network requests.

## Activity

The chart is a static, theme-aware SVG generated from current public repository commits. Its title, native recent-commit links, and snapshot label describe the scope. Counts include repository commits rather than claiming personal contributions or expertise. The profile's own automation commits are excluded.

GitHub supports the native anchors, `picture`, `details`, and media queries used here. It removes arbitrary scripts and styles from README content, so swipe controls, interactive chart tooltips, and frame-dependent GIF links are not promised. A separate website would be required for those controls.
