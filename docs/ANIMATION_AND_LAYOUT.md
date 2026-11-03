# Profile layout and motion

The profile keeps contacts, project notes, and statistics native. Four section title images retain the graphite, white, muted blue/red, Inter, and square-outline styling. Theme tokens live in config/profile.json. The existing project carousel and activity section are unchanged.

## Identity and titles

The existing 128 x 128 framed avatar SVG is embedded byte-for-byte in the responsive header, displayed proportionally at 176 px on desktop and 112 px on mobile. Name and role use the previous native system-font family inside SVG text. The name is strongest, followed by the exact role Software Engineer. A complete alt description preserves accessible identity and stack text. Hourly refresh still downloads and frames the current avatar; header composition embeds the updated frame. Original supplied assets remain untouched.

Projects and Projects list retain desktop/mobile title strips. Compact 30 px image titles label both disclosures. The standalone Tech stack and AI Development Tools sections have been removed; their old assets remain available. Picture wrappers preserve summary toggles, and the Projects list anchor preserves carousel navigation.

## Header and technology motion

The header uses a transparent self-contained SVG composition, selected through GitHub-compatible picture sources. This avoids custom flex/grid CSS and visible layout-table borders. At 768 px and below it selects a stacked composition. Natural image widths and GitHub's max-width rule prevent overflow. Native GitHub Repositories and LinkedIn anchors sit underneath, independently clickable with mouse or keyboard. A transparent spacer aligns them with the information block on desktop and collapses on mobile. Buttons are 44 px tall.

The technology carousel is configured in config/tech-stack.json. Java, Spring Boot, PostgreSQL, Docker, and OpenAI Codex are preserved, and Python is added. REST APIs/Authentication are retained only as unused configuration metadata, removed from the visible header and its alt description. Unity stays in the Potamorph project notes. Codex is labeled AI tool, using its vendor's recognizable OpenAI knot.

The desktop portrait is separated from the name/title/carousel block by a vertical silver line. One long horizontal line spans the information column below the carousel, with the supplied reference's short white center highlight. Both native contact links sit side by side, centered beneath that line, with no line between the buttons. The upper-right decoration stays beside the name; the lower-left decoration is on the footer row, beside the buttons. The stacked mobile layout retains the horizontal rule above the contacts and omits the desktop portrait divider. Decorations are static, transparent SVG paths with theme-aware contrast. Contact button widths are 160 and 96 px and remain readable at 320 px viewport width.

Each evenly spaced item contains a 32 px official logo above a 12 px Inter label. Labels are rasterized at 2x using the bundled font; logos stay vector. The viewport is 600 x 88 on desktop and 288 x 88 on mobile. A single linear SMIL track moves from minus one sequence width to zero in 30 seconds. Enough exact copies cover the viewport even for a one-item stack; the start and end pixels match. A transparent alpha mask gently fades the edges. There is no background rectangle, item card, or glow.

Reduced motion selects a static grid with every technology visible. Light and dark variants preserve contrast. The complete animated header is about 101 KB, including the untouched framed avatar and embedded carousel. Only the selected variant loads. The standalone carousel is about 43 KB. SVG animation was tested inside an actual image element, including the nested carousel, so no GIF fallback is required by the observed behavior. This local revision has not been published.

## Carousel

One centered image holds Vigil for three seconds, slides to Potamorph in 400 ms, and loops in 6.8 seconds. Reduced motion switches every three seconds without sliding. The entire image links to #projects-list; native project links open each repository's blob/main/README.md.

Desktop uses 1000 x 380; mobile uses 480 x 450. The outer frame is square. Vigil retains its light-blue blueprint surface; Potamorph retains its teal/rust identity. Both show name, short description, and the unchanged official logo. Their Explore projects footer is embedded once below the moving track.

Self-contained SVG embeds lossless PNG slides. No JavaScript or external SVG images are required. A visitor loads one approximately 372 KB desktop or 259 KB mobile variant. A static preview remains inside Project notes. The prior frozen reduced-motion PNG is replaced by automatic non-sliding changes.

## Activity and avatar refresh

The API updater renders native per-project 30-day commits and stars, with a visible successful-fetch timestamp. It excludes profile automation. The same hourly workflow fetches the current avatar. All network requests and rendering finish before replacing valid files. Failed requests preserve the previous valid profile; successful fetches advance the timestamp even when counts stay unchanged.
