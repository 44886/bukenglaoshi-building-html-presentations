---
name: bukenglaoshi-building-html-presentations
description: Use when creating or editing a slide deck, presentation, pitch, keynote, report, or slideshow that must be delivered as one standalone HTML file.
metadata:
  version: 1.0.1
---

# Building HTML Presentations

Create a presentation, not a scrolling website. The final artifact is one portable `.html` file with a stable 16:9 stage, reliable page navigation, content-appropriate motion, and every local runtime asset embedded. Visual direction must follow the audience and subject; a launch-event look is one optional family, never the universal default.

## Non-Negotiable Contract

- Deliver one HTML file. Inline CSS, JavaScript, JSON, SVG, fonts, ECharts, and local media; convert local binary assets to data URIs.
- Do not use CDNs, external scripts, remote stylesheets, hotlinked media, or adjacent runtime files.
- A remote webpage is the sole network exception. Mark it `data-network-required="true"`, include `.embed-fallback`, disclose the dependency, and prefer an offline `srcdoc` snapshot when possible.
- Preserve the user's page order, wording, facts, required assets, and brand constraints. Do not invent business claims or replace missing content with filler.
- Keep the top progress bar, page counter, keyboard/buttons/touch navigation, reduced-motion behavior, print layout, and responsive viewport scaling.
- Support keyboard-emulating presentation clickers: PageUp/PageDown and arrow keys are the guaranteed baseline; Enter, Space, Backspace, and recognized next/previous media or browser keys must also navigate.
- Treat staged content as presentation steps. Every forward input reveals one pending `.fragment` or presenter-controlled timeline step before changing pages; every backward input first retracts one revealed step. Buttons, keyboard/clicker keys, touch swipes, and wheel navigation must share this behavior.
- Default to no staged reveals. Add manual steps only when seeing later content early would distract from the current point, spoil a conclusion, or break a necessary sequence. Covers, agendas, reference lists, checklists, and peer comparisons normally appear at once; keep the total click burden proportionate to the talk.
- Use at most one primary motion mechanism per page. Three manual steps is the normal ceiling; four or five require a clear spoken sequence, and more than five should become another page. Do not fragment titles, eyebrows, captions, ordinary body copy, or decorative shapes. A fragment must be a complete semantic beat, and related elements should reveal together.
- Entering a page forward starts its manual steps hidden. Returning from the next page shows the previous page in its completed state so repeated backward inputs can retract its steps. Page counter, progress, and URL hash change only when the page changes.
- Use `data-shared` for meaningful objects that recur across pages. Shared motion must support View Transitions and a measured fallback.
- Treat style as a visual system, not a page template. Layout follows the page's content role; do not default to equal cards, decorative panels, or repeated split screens.
- Never infer “premium” to mean dark launch-event styling. Editorial, information-design, human, technical, playful, cinematic, and product-system families are equal first-class options. Load launch-event rules only when the user selects that direction or the brief explicitly calls for a flagship reveal.
- Keep reference/photo pages complete on entry. Checklists, contact details, homework, instructions, and take-home guidance should not require the audience to reconstruct the page from animation.
- For edits, target stable slide IDs and preserve approved pages. Insertions, deletions, reorders, and duplicated covers must remain idempotent when the deck is rebuilt.

## Workflow

1. Read the complete request and existing artifact. Use [references/content-architecture.md](references/content-architecture.md) to identify audience, purpose, presentation mode, room/screen conditions, photo-taking needs, assets, privacy, and time. Maintain a content ledger of supplied facts, approved wording, page order, deletions, and later corrections. Ask only for missing information that materially changes the output.
2. Make a page map with stable IDs and roles: cover, claim, chapter, evidence, chronology, comparison, process, reference/photo, gallery, or conclusion. Preserve the user's explicit page order. Resolve density through editing, grouping, hierarchy, composition, or page splits before shrinking type.
3. If no style is fixed, read [references/style-catalog.md](references/style-catalog.md). Offer three context-relevant numbered choices from genuinely different visual families, including mood, best use, and 3-4 swatches; expand to at most six only when the user asks for broader exploration. Recommend one and wait unless the user delegates the decision. If the user explicitly asks for an Apple/Xiaomi-style launch, flagship keynote, or premium stage reveal, then read [references/launch-event-style.md](references/launch-event-style.md). Do not load it merely because the subject is technology or the user asks for a polished result.
4. Read [references/deck-spec.md](references/deck-spec.md), create or update the JSON specification, and use semantic HTML. Read [references/component-catalog.md](references/component-catalog.md) only for components needed by the page map. Create a motion inventory with page ID, primary mechanism, narrative purpose, and manual-step count. Default to zero manual steps; remove motion without a specific narrative function.
5. Use local asset files in the spec as `asset:relative/path.ext`. Follow active image-generation instructions when new visuals are needed. Prefer evidence and subject matter over decorative filler. Inspect crops and personal information before embedding.
6. Build and validate:

```powershell
python <skill-dir>/scripts/build_presentation.py deck.json --out presentation.html
python <skill-dir>/scripts/validate_deck.py presentation.html
```

7. Open the result in a real browser and follow the acceptance matrix in `content-architecture.md`. At minimum verify the cover, densest photo/reference page, densest evidence page, every chart, all justified internal steps forward and backward, focus geometry, round-trip layout stability, counter/progress/hash behavior, 1440x900 desktop, narrow mobile, reduced motion, print/static comprehension, image dimensions, offline behavior, and console errors.

For changes to the bundled builder or runtime, also run the unit tests in `tests/` and the portable Playwright suite in `tests/browser/`. The browser suite builds `examples/demo-deck.json` into a temporary directory; install its declared development dependency first and set `PLAYWRIGHT_BROWSER_EXECUTABLE` only when using an existing browser binary.

## Component Routing

| Need | Use |
|---|---|
| Audience, page roles, density, step decisions, edits, acceptance | `references/content-architecture.md` |
| Visual direction | `references/style-catalog.md` |
| Apple/Xiaomi-style launch event or flagship keynote | `references/launch-event-style.md` |
| JSON fields, assets, notes | `references/deck-spec.md` |
| ECharts, timeline, count-up, iframe, media, tables | `references/component-catalog.md` |
| Working runtime | `assets/presentation-template.html` via builder |

## Common Failures

- **Single file in name only:** Local CSS, images, fonts, or scripts still sit beside the HTML. Rebuild through the asset embedder and rerun validation.
- **Web page instead of deck:** Continuous vertical scrolling, fluid section heights, or marketing navigation. Keep one fixed scene visible at a time.
- **Fake shared motion:** A global logo moves while repeated content snaps. Give matching semantic objects the same `data-shared` key on both pages.
- **Chart screenshots:** Use embedded ECharts for data-driven visuals unless the user explicitly requests a static image.
- **Remote iframe presented as offline:** Use `srcdoc` or disclose that the iframe needs a network and may be blocked by `X-Frame-Options` or CSP.
- **Animation everywhere:** Motion should communicate page hierarchy, chronology, or object continuity. A page does not earn fragments merely because it contains several items. Respect reduced motion and avoid looping decoration.
- **AI-template composition:** A decorative left rule beside text plus a detached rectangle, equal cards without peer-level information, filler panels, meaningless gradients or shapes, repeated 50/50 splits, and default dark dashboards are not acceptable composition strategies. Use hierarchy, evidence, images, diagrams, type, and negative space according to the page's content role.
- **Dark template mistaken for a launch event:** Black backgrounds, orange text, visible grid lines, boxed counters, and a row of persistent controls still read as presentation software. A flagship-keynote direction requires a quiet stage, typography-led claims, evidence without card frames, and one controlled focal motion. Follow `references/launch-event-style.md`.
- **Every page looks unrelated:** Content-driven variation still needs one grid, type system, palette, and motion language across the deck.
- **Reference page cannot be photographed:** Important items appear only after clicks or are spread across transient states. Show the complete reference view on entry and use page-level entrance motion only.
- **Incremental edit drifts the deck:** A change addressed by page number duplicates or reorders content after later inserts. Use stable slide IDs and rebuild from the JSON source of truth.

## Completion Gate

Do not report completion until the builder and validator exit successfully, representative browser screenshots are nonblank, clicker navigation obeys the fragment-first state contract, charts contain rendered pixels, required images decode, and every explicit user requirement is mapped to observable evidence. For transformed or focus-based pages, measure the focal element against the stage center and compare its geometry before and after a forward/backward round trip. Deliver the final HTML and keep the editable JSON specification beside its local assets.
