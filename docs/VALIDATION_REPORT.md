# Validation report

Checked locally on 3 November 2026, after selecting Engineering Blueprint and correcting Potamorph's positioning to AI-tool usage.

- Complete README, desktop/mobile assets, complete static fallbacks, authoring sources, build scripts, and local profile previews were generated.
- GitHub's actual Markdown API rendered the final README. Its sanitizer preserved the required standard HTML attributes and media sources.
- Browser checks passed at 320, 390, 600, 601, 768, 1024, and 1280 px. No horizontal overflow, wrapped panels, or visible row gaps were measured; seam tolerance was below 0.1 CSS px.
- Light and dark GitHub styles were checked. All seven hero links passed actual pointer and keyboard activation.
- Reduced motion selected PNGs at every tested width, including the mobile/desktop breakpoint.
- The hero was also injected locally into an existing GitHub page for a read-only check against its live CSS and custom elements. Assets were intercepted locally; no repository content was modified.
- Each variant has a 10.4-second timeline. All 130 decoded samples of its linked GIF panels reassemble exactly into the corresponding full network movie.
- Boundary pixels remain identical across every sample, and the loop's final/first frame mean difference is zero.
- Desktop linked GIFs total **180,857 bytes**; mobile linked GIFs total **217,818 bytes**. A browser selects one variant. The complete image collection includes additional static fallbacks and optional master reference movies.
- Configured routes terminate exactly at the core and project ports and use only right-angle or 45° segments.
- Every local image path exists. All six distinct GitHub destinations returned HTTP 200, including both repositories and their commit pages. Fragment targets are supported by the referenced README headings.
- Personal skills exclude Unity and C#. Potamorph is identified as an AI development case study. OpenAI Codex is explicitly categorized under AI Development Tools.
- The supplied personal logo and bundled font sources match their recorded SHA-256 hashes.

Machine-readable results are in `assets/previews/blueprint/browser-report.json` and `validation-report.json`. Rebuilds regenerate the evidence; this human report records the checked design and compatibility decisions.

## Limits

Independent GIF starts can drift; invariant boundaries preserve geometry without promising frame-perfect timing. The precomposed master is the synchronized reference.

The image hero preserves custom typography but is not selectable text. Accessible alt text and native Markdown provide the same project and skills information. Very narrow layouts receive a separately composed mobile diagram.

The checks recorded above were performed before publication. They used actual server-rendered Markdown and live GitHub styling, with locally served assets. These checks alone do not establish GitHub's eventual image proxy/cache behavior; the public profile must also be checked after upload.

LinkedIn was verified as the public profile's listed link; automated access to LinkedIn contents is not required by the profile. No email address or unsupported contact information was invented.

GitHub activity uses native contribution and commit links, avoiding third-party statistics services and fabricated activity counts.

## Published profile verification

Published on 3 November 2026 to the public [profile repository](https://github.com/slavisa-simic/slavisa-simic), on its `main` branch. The README is visible directly on the [GitHub profile](https://github.com/slavisa-simic).

The actual public profile was checked in an unauthenticated browser at 1440 px and 390 px. The published README matches the approved local file. Every hero image loaded from the public repository, all seven linked regions had the expected destinations, responsive sources selected the correct desktop/mobile assets, and no panel or row seams were measured. Reduced motion selected the published PNG fallbacks successfully.

Screenshots and the machine-readable public verification report are retained locally under `assets/previews/blueprint/published-*`. This check used the published profile and its real public assets, without replacing page contents or intercepting image requests.
