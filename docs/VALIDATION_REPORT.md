# Clean developer profile validation

Checked on 3 November 2026 against the supplied blueprint reference.

- Name, roles, contacts, and statistics remain selectable text. The current GitHub avatar has a sharp frame; original supplied S and project marks remain unchanged.
- Six titles are images with alt text. Major strips have mobile compositions. Summary images toggle their disclosures; the carousel retains its Projects list target.
- The palette matches the reference. The carousel has square corners and retains both distinct project identities and the shared footer.
- Shields.io badges cover Java, Spring Boot, PostgreSQL, Docker, and OpenAI Codex. Codex stays under AI Development Tools. Unity/C# remain project details.
- All four carousel variants retain three-second holds, the loop clone, and unchanged proportional logo composites. Reduced motion changes projects automatically without sliding.
- Eleven unit tests cover activity boundaries, pagination, private/profile exclusion, timestamps, no-op offline builds, escaping, empty windows, original avatar downloads, changed avatar bytes at an unchanged URL, and failure preservation.
- Nine viewport widths from 320 to 1440 pass local overflow, image loading, navigation, disclosure, and motion checks. Framing preserves exact downloaded avatar bytes.

Machine-readable browser, animation, media, and public-profile evidence is kept locally in assets/previews/profile.

The published profile passed actual GitHub browser checks at 1440, 390, and 320 px, including both motion preferences, working image-title disclosures, carousel navigation, and direct project README links. The [hourly workflow](https://github.com/slavisa-simic/slavisa-simic/actions/runs/41723034674) passed all eleven tests, fetched public activity and the current avatar, and created [automated commit a8acc53](https://github.com/slavisa-simic/slavisa-simic/commit/a8acc53). Its successful sync advanced to 21:34:50 UTC. The avatar checksum remained unchanged, so its existing content-addressed frame was correctly reused. A simulated changed image at the same GitHub URL verifies automatic frame replacement without altering the real account picture.
