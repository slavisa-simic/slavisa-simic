# GitHub profile override

These rules override the generated master because this surface is a GitHub README. The current user request takes precedence over previous layout decisions.

- Preserve graphite #101113/#141619, white #edf0f4, blue #82a9d5, red #cc8a88, hairline frames, and the original avatar and project marks.
- Identity: align the name, Software Engineer, and Backend & full-stack development on one left edge. Use weights 700, 500, and 400. No accent rule beside the third line. Native contact buttons align with this text column and remain separately keyboard-accessible.
- Stack the identity at 960 px and below. Keep the personal technology list separate from project technologies. Codex is an AI development tool; Unity/C# belong to Potamorph's project stack.
- Preserve the existing animated project cards. Hold for three seconds and slide in 400 ms; reduced motion switches without sliding. Center one footer indicator per project, with no Explore projects label.
- Keep the technology marquee moving right in both system motion settings, following the user's explicit preference. Optional static exports are not automatically selected.
- Retain the simple About Me description: I build backend services and full-stack applications.
- After the carousel, show a project table with each public project, its real source image, short factual description, features, and actual stack. Adapt the visual reference to the existing palette; do not invent cloud deployments or achievements.
- Repository buttons open the matching repository root. Demo placeholders have no link. Keep all interactive links native, independently clickable, and keyboard-accessible.
- Use responsive project artwork for readable mobile layouts inside a GitHub-compatible native table. Bundle source captures and provenance. Essential image text needs a complete alt equivalent.
- Remove the old Projects list, commit/star statistics, sync footer, project notes, recent changes, and workflow badge from the visible README. Retain background avatar/activity collection without showing those sections.
