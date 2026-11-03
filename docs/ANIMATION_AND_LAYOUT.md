# Native profile layout and motion

The terminal theme uses native selectable text for identity, contacts, shell-style headings, and repository statistics. The preserved S mark, cached Shields.io badges, and project carousel are separate visual assets. Notes and raw commit messages remain in disclosures.

## Identity

The supplied S mark retains its silver ribbon and fold shading. It is the only image in the header. Name, roles, prompt, and contacts are native HTML text styled with samp, so they remain selectable, searchable, and responsive. The former identity SVG/PNG text assets are removed.

## Projects carousel

One centered image shows Vigil, slides horizontally to Potamorph, and loops. The whole carousel links to the visible `Projects list` heading below it. Each native list entry links directly to its project's `blob/main/README.md`, with no section fragment. There are no pretend previous/next buttons.

The desktop carousel is 1000 × 380 px; mobile uses a 480 × 450 composition. Each project is held for three seconds. A 400 ms eased translation produces a 6.8-second loop. Reduced motion uses instant project changes at three-second intervals with no moving transition, producing a six-second loop. Both variants repeat automatically.

Both supplied official logo PNGs remain byte-for-byte intact. Vigil has a light blue blueprint surface; Potamorph has a darker teal/rust treatment. Each card explicitly displays its name, short description, and original logo. The shared Explore projects footer is embedded once below the moving track, so it stays identical throughout the carousel.

The self-contained SVG embeds lossless PNG slides. It needs no JavaScript, external images, or GIF palette reduction. A browser loads one approximately 369 KB desktop or 257 KB mobile variant. Native project links remain visible independently of animation. A static preview is available inside Project notes.

The reported non-advancing carousel was reproduced in the in-app browser: reduced motion was true and its selected image was `projects-carousel.png`. The revised picture source selects the non-sliding animated SVG in this mode. Verification must test the actual default preference as well as forced normal motion.

## Activity

The API updater generates native table cells for each project's 30-day commit count and stars. The last successful sync time is visible beside the hourly refresh label. These are real repository counts, and profile automation is excluded. No statistics image is used. Every successful scheduled fetch updates the timestamp; failures preserve the preceding valid profile.

GitHub supports the native anchors, `picture`, `details`, and media queries used here. JavaScript is excluded from README content, so the carousel uses SVG motion with one stable external anchor. Body content stays native and keyboard accessible.
