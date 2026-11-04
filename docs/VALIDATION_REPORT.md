# Profile layout validation

Validated locally through GitHub-rendered Markdown and current GitHub styles. The cached avatar and activity snapshot were reused. Changes remain in the local checkout.

- The name, Software Engineer, and backend/full-stack line share one left edge and use weights 700, 500, and 400. There is no accent rule beside the third line.
- Native contact buttons align with the identity text column on desktop and with the stacked text on smaller screens. The header stacks at 960 px before its artwork would need scaling.
- The new project table contains Vigil and Potamorph, including real project captures, factual descriptions, feature labels, and actual technology stacks. The table fills the content width.
- Each Repository link opens the matching repository root. Pointer and keyboard navigation pass. Each Demo image has no enclosing anchor and cannot navigate.
- Projects list, commit/star statistics, the sync timestamp, project notes, recent changes, and the workflow badge are absent from the visible README.
- Nine checked widths pass without horizontal overflow or missing images: 320, 375, 390, 600, 601, 768, 844, 1024, and 1440 px. Light/dark variants and enlarged native text also pass.
- Fifteen unit tests pass, including cached rebuild stability, activity boundaries, avatar replacement, failure preservation, and the hidden activity presentation.
- All four project carousel variants pass their hold, transition, loop, image playback, and centered active-indicator checks. The original proportional logo composites remain exact.
- The technology marquee passes constant rightward speed, seamless repeating pixels, transparency, and actual README image playback in all eight size/theme/system-motion combinations.
- Source capture hashes, avatar bytes, icon caches, embedded assets, and media budgets pass validation. Git diff whitespace checks pass.
- The hourly workflow rebuilds project rows, project carousel assets, and the technology marquee before refreshing the avatar.

Review screenshots and reports are under assets/previews/profile/ (ignored by Git): desktop.png, mobile.png, light.png, browser-report.json, animation-report.json, tech-animation-report.json, and validation-report.json. Source captures and provenance are bundled under assets/profile/source/.
