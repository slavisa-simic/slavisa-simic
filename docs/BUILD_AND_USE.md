# Build and use the Engineering Blueprint profile

The approved design is implemented in the root `README.md`. Potamorph is presented as an **AI development case study**, with OpenAI Codex under **AI Development Tools**. Unity and C# describe the resulting prototype; neither is listed as personal expertise.

## Ready-to-use files

`dist/profile-ready.zip` contains only the README and the assets it needs. Extract its contents into the root of the profile repository while preserving the `assets/blueprint/` paths. Keep the full source locally or use `dist/profile-source.zip` if you want the reproducible pipeline in the repository as well.

For GitHub to display the README on the profile, the public repository must be named `slavisa-simic`, owned by `slavisa-simic`, with `README.md` at its root. See [GitHub's profile README instructions](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme).

The profile belongs in `slavisa-simic/slavisa-simic`. Publish subsequent updates by committing the rebuilt README and assets to that repository's default branch. Keep the build sources alongside them so the design can be reproduced.

## Rebuild

Use Python 3.11+ and Node.js 20+. On Windows, the installed Python launcher is `py`; use `python` in environments where that command selects your interpreter.

```powershell
py -m pip install -r requirements.txt
npm ci
npx playwright install chromium
py scripts/build.py --preview --package
```

The renderer can reuse an installed Playwright Chromium, or accept `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH`. Fonts and the supplied personal logo are bundled, so asset generation needs no font service or image-generation API. The first `--preview` run needs internet access for GitHub's Markdown renderer and stylesheets.

For a focused rebuild, run these stages in order:

```powershell
py scripts/build_assets.py
node scripts/render_assets.mjs
py scripts/generate_animations.py
py scripts/build_readme.py
node scripts/render_preview.mjs
py scripts/validate_layout.py --check-links
py scripts/package_profile.py
```

The build script runs these checks except the optional external-link recheck. It does not publish anything.

## Edit the profile

- Change identity copy, personal skills, AI tool disclosure, project labels, ports, and routes in `config/network.json`.
- Edit readable profile descriptions in `src/README.template.md`.
- Edit the approved visual grammar in `src/blueprint.css` and `src/blueprint.mjs`.
- Rebuild instead of editing generated README HTML or image files.

## Previews and evidence

- `assets/previews/blueprint/profile.html`: entire profile, rendered through GitHub's Markdown API.
- `assets/previews/blueprint/profile-desktop.png` and `profile-mobile.png`: complete profile screenshots.
- `assets/previews/blueprint/profile-light.png`: light-theme rendering.
- `assets/previews/blueprint/github-live-hero.png`: read-only test inside a live GitHub page using its actual styles.
- `assets/blueprint/desktop/hero-static.png`: complete static hero.
- `assets/previews/blueprint/browser-report.json` and `validation-report.json`: measured results.

The HTML preview opens locally and references saved stylesheets and local image files. The source ZIP includes these dependencies. It is a review artifact, not a separate portfolio website.
