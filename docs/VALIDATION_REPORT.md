# Header and technology carousel validation

Validated locally for the requested header refinement. This revision has not been published, committed, or pushed. The existing activity snapshot and successful-sync timestamp were reused.

- The title is exactly Software Engineer. The accessible description includes the name, complete stack, and Codex's AI development tool category.
- Java, Spring Boot, PostgreSQL, Docker, and Codex are preserved; Python is added. Codex keeps its AI tool caption. REST APIs and Authentication are removed from the visible header and its alt text. Unity is absent from personal skills and remains in the unchanged Potamorph notes. The upper-right decoration moves 48 px farther outward on desktop.
- The desktop portrait has a vertical divider beside the information block. A long horizontal line sits below the carousel and above the two centered, independently clickable contacts. There is no separator between the contact buttons. The upper-right decoration is beside the name; the lower-left decoration sits on the desktop contacts row. The stacked mobile layout keeps the horizontal rule and side-by-side contacts. Decorations retain real transparency and adapt to light mode.
- The standalone Tech stack and AI Development Tools sections are removed. Historical title/badge assets remain available.
- The original framed avatar SVG, cached avatar bytes, personal logo, project cards, activity snapshot, project list, notes, and recent changes match their pre-edit repository content. Each composed header embeds the exact framed avatar SVG.
- Fifteen unit tests pass, including automatic sizing for a longer technology label, one-item viewport coverage, invalid configuration, moving-only header sources, existing activity boundaries, no-op rebuilds, and changed avatar bytes at an unchanged URL.
- GitHub's Markdown API preserves the picture sources and independent contact anchors. Current GitHub styles pass nine widths: 320, 375, 390, 600, 601, 768, 844, 1024, and 1440 px. There is no horizontal overflow, missing image, or broken project/statistics table. The header stacks at 768 px and below. Light theme, reduced motion, enlarged native text, disclosures, and mouse/keyboard navigation pass.
- The four moving technology variants use one continuous linear translation from minus one sequence width to zero over 30 seconds. Measured displacement confirms rightward motion and constant speed. Screenshots at matching phases on consecutive cycles are pixel-identical, including the exact loop boundary. Duplicate sequences cover the viewport without gaps.
- Actual image-element playback passes for both composed header sizes, including nested SVG animation. Canvas sampling confirms fully transparent and partially transparent pixels. No GIF fallback is needed for the tested rendering path.
- The static-header issue was reproduced on the live profile: normal motion selected the animated SVG while reduced motion selected a static grid. The updated README always selects a moving header. Actual README image playback passes all eight desktop/mobile, light/dark, and system motion combinations. Optional static exports remain available. The separate project carousel retains its existing motion preferences.
- SVG icon provenance hashes and Devicon MIT/Simple Icons CC0 notices are bundled. Each standalone tech asset is under 100 KB; the selected composed header is about 101 KB. Builds work offline with the bundled cache and fonts.
- The workflow rebuilds on stack, source, font, or icon changes and hourly. An offline repeat rebuild is a no-op. Git diff whitespace checks pass.

Review artifacts are in `assets/previews/profile/` (ignored by Git):

- `header-desktop.png`, `header-mobile.png`: sanitized README previews with normal motion selected.
- `header-desktop-reduced.png`, `header-mobile-reduced.png`: captures with the system reduced-motion preference enabled; the technology marquee stays animated.
- `desktop.png`, `mobile.png`, `light.png`: complete README captures.
- `browser-report.json`, `tech-animation-report.json`, `animation-report.json`, `validation-report.json`: machine-readable verification.

Local checks establish GitHub-sanitized markup and browser image playback. Live verification of this revision awaits an approved publication. See BUILD_AND_USE.md for the documented SVG composition compromise and instructions for adding technologies.
