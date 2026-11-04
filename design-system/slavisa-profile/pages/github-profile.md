# GitHub profile override

These rules override the generated master because this surface is a GitHub README. The current user request takes precedence over previous layout decisions.

- Preserve graphite #101113/#141619, white #edf0f4, blue #82a9d5, red #cc8a88, hairline frames, and the original avatar and project marks.
- Identity: align the name, Software Engineer, and Backend & full-stack development on one left edge. Use weights 700, 500, and 400. No accent rule beside the third line. Native contact buttons align with this text column and remain separately keyboard-accessible.
- Stack the identity at 960 px and below. Keep the personal technology list separate from project technologies. Codex is an AI development tool; Unity/C# belong to Potamorph's project stack.
- Preserve the existing animated project cards. Hold for three seconds and slide in 400 ms; reduced motion switches without sliding. Center one footer indicator per project, with no Explore projects label.
- Keep the technology marquee moving right in both system motion settings, following the user's explicit preference. Optional static exports are not automatically selected.
- Retain the simple About Me description: I build backend services and full-stack applications.
- Group the carousel and table under one native Projects heading. No All projects heading, feature tags, or colored left accents. Each public project has its real screenshot, selectable native heading, category, short description, optional note, and cached technology badges. Do not invent cloud deployments or achievements.
- Repository buttons open the matching repository root. Demo placeholders have no link. Keep all interactive links native, independently clickable, and keyboard-accessible.
- Use a desktop-focused native four-column table: screenshot, description, technology badges, and vertically stacked actions. Center the screenshot horizontally and vertically in its cell. Project names and prose must never be flattened into images. Bundle source captures, badge SVGs, and provenance; images retain appropriate alt descriptions. Horizontal table scrolling on narrow screens is acceptable.
- Remove the old Projects list, commit/star statistics, sync footer, project notes, recent changes, and workflow badge from the visible README. Retain background avatar/activity collection without showing those sections.
