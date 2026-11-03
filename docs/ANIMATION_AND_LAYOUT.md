# Profile layout and motion

The clean developer layout keeps identity, contacts, project notes, badges, and statistics native. Six title images follow the supplied blueprint reference: graphite, white, muted blue/red, Inter, and square outlines. Theme tokens live in config/profile.json.

## Identity and titles

The current GitHub avatar is embedded unchanged in a 128 x 128 square SVG frame, displayed at 112 px. Name, roles, and contacts remain selectable. Hourly refresh downloads the avatar even when its source URL stays unchanged. Changed image bytes create a fresh generated URL; original supplied assets remain untouched.

Projects, Projects list, and Tech stack have 860 x 50 desktop and 360 x 46 mobile strips at triple resolution. Compact 30 px image titles label AI Development Tools and both disclosures. Alt text provides accessible names. Picture wrappers prevent GitHub from turning summary images into download links. An explicit Projects list anchor preserves carousel navigation.

## Carousel

One centered image holds Vigil for three seconds, slides to Potamorph in 400 ms, and loops in 6.8 seconds. Reduced motion switches every three seconds without sliding. The entire image links to #projects-list; native project links open each repository's blob/main/README.md.

Desktop uses 1000 x 380; mobile uses 480 x 450. The outer frame is square. Vigil retains its light-blue blueprint surface; Potamorph retains its teal/rust identity. Both show name, short description, and the unchanged official logo. Their Explore projects footer is embedded once below the moving track.

Self-contained SVG embeds lossless PNG slides. No JavaScript or external SVG images are required. A visitor loads one approximately 372 KB desktop or 259 KB mobile variant. A static preview remains inside Project notes. The prior frozen reduced-motion PNG is replaced by automatic non-sliding changes.

## Activity and avatar refresh

The API updater renders native per-project 30-day commits and stars, with a visible successful-fetch timestamp. It excludes profile automation. The same hourly workflow fetches the current avatar. All network requests and rendering finish before replacing valid files. Failed requests preserve the previous valid profile; successful fetches advance the timestamp even when counts stay unchanged.
