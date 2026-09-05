# Content Architecture and Interaction

Use this reference before choosing layouts or animation. It turns raw page-by-page material into a deck that works for the audience, the presenter, and later incremental edits.

## Start With the Viewing Situation

Capture these decisions from the request. Infer obvious answers and ask only when a missing answer would materially change the result.

| Decision | Why it matters |
|---|---|
| Purpose and audience | Determines tone, evidence, vocabulary, and density |
| Presenter-led or self-paced | Determines whether manual reveals are useful |
| Room viewing or personal screen | Determines type size, contrast, and control visibility |
| Audience may photograph pages | Requires complete, static reference pages |
| Time available | Limits page count and click burden |
| Existing deck or new deck | Determines whether slide order and IDs must be preserved |
| Supplied assets and privacy | Determines download, crop, redaction, and offline packaging work |

Treat the user's exact wording, supplied facts, order changes, and approved pages as a content ledger. Do not silently resurrect deleted material or rewrite an approved claim during later edits.

## Give Every Page a Role

Choose the page role before choosing a component. The same visual system can support different compositions.

| Page role | Typical composition | Default reveal policy |
|---|---|---|
| Cover | full-bleed image or strong typographic field | all at once |
| Claim | one statement with a decisive keyword or line | one reveal only when it completes the claim |
| Chapter divider | short transition statement | all at once |
| Evidence | chart, document, image, quote, or artifact leads | evidence and interpretation may reveal as two beats |
| Chronology | linear timeline or horizontal focus sequence | one step per spoken milestone when presenter-led |
| Comparison | shared axis, paired fields, or before/after | reveal the second side only when contrast is the point |
| Process | numbered sequence, flow, or demonstration | ordered steps when sequence matters |
| Reference/photo page | checklist, guidance, contacts, homework, summary | always complete on entry |
| Gallery | several images with one current focus | one focus change per image when the presenter discusses them |
| Conclusion | final synthesis, decision, or invitation | all at once unless the last line is a deliberate reveal |

Do not force every page into a card grid, 50/50 split, or repeated title-plus-box shell. Reuse the deck's grid, spacing, type, palette, and motion language while allowing the page role to determine composition.

## Decide What Belongs on One Page

Use this order when a page feels crowded:

1. Remove repetition and turn sentences into short spoken-support phrases.
2. Group details under two to four meaningful headings.
3. Promote one message and demote supporting material.
4. Change the composition: diagram, shared-axis chart, evidence image, or reference sheet.
5. Split the page only when it contains more than one argument.
6. Reduce type size last, and never below the runtime's readable baseline.

Keep related evidence together. Two curves that answer one comparison belong on the same axes. Events that happened in different years remain separate milestones. A list the audience may photograph should remain on one complete page even when it is denser than surrounding claim pages.

## Decide Whether to Add a Manual Step

Default to no fragments. Add one only when at least one answer below is yes:

- Would seeing the later content early spoil a conclusion, answer, contrast, or emotional beat?
- Is the presenter explaining a true chronology, process, dialogue, or image sequence one item at a time?
- Does the layout itself change meaningfully, such as one centered idea becoming a two-sided comparison?

Do not add a manual step when the content is a checklist, contact sheet, agenda, reference table, homework list, operating instruction, or photo-taking page. Do not fragment titles, captions, decorative marks, or peer facts only to make the page feel animated.

Create a motion inventory before implementation:

| Page ID | Role | Primary motion | Narrative purpose | Manual steps |
|---|---|---|---|---:|
| `purpose` | claim | keyword reveal | withhold the conclusion | 1 |
| `resume` | chronology | horizontal focus | discuss one year at a time | 6 |
| `reading-guide` | reference/photo | page entrance only | audience photographs full guidance | 0 |

Three manual steps is the normal ceiling. Four or five require a real sequence; a longer chronology is acceptable when every click maps to one spoken milestone. Count total clicks for the whole talk, not only per page.

## Presenter-Controlled Interaction Contract

All navigation inputs must use one state machine:

1. Forward reveals or advances exactly one internal step.
2. Forward changes page only after the current page is complete.
3. Backward first retracts exactly one internal step.
4. Returning from the next page restores the previous page in its completed state.
5. Counter, progress, and URL hash change only when the page changes.

This contract applies to PageUp/PageDown, arrow keys, Enter, Space, Backspace, recognized clicker media/browser keys, buttons, wheel gestures, and swipes.

For focus timelines and galleries, compute placement from geometry. Translate the track until the active item's bounding-box center equals the stage center. Derive scale, opacity, and blur from distance to the active item. Never accumulate transforms across visits; state must be recomputed from the active index so leaving and returning cannot shift the layout.

## Assets, Evidence, and Privacy

- Download permitted remote images into the deck source folder, then embed them through `asset:` tokens. The final HTML must not hotlink them.
- Prefer real evidence supplied by the user over decorative generated imagery.
- Use `object-fit` intentionally and inspect the actual crop at presentation size.
- Check certificates, chat screenshots, class lists, phone numbers, and other personal material for unintended exposure. Preserve user-requested contact details, but do not expose unrelated information visible in source images.
- Give every meaningful image accurate alt text and verify nonzero natural dimensions.

## Incremental Editing

- Keep the JSON specification as the editable source of truth.
- Give every slide a stable semantic `id`; target changes by ID, not by current slide number.
- Preserve approved slides unless the user asks to restyle them globally.
- Insert, reorder, replace, or delete exactly once. Re-running the edit must not duplicate pages, fragments, or assets.
- After a reorder, recalculate counters automatically and retest any cross-page shared transitions.
- Keep a final cover copy as a separate slide ID when the user requests a repeated ending; do not alias the same DOM node.

## Browser Acceptance Matrix

Verify source rules and visible behavior:

| Area | Required check |
|---|---|
| Framing | 1440x900 and a narrow viewport; no clipping, overlap, scrollbars, or text outside the stage |
| Density | cover, densest reference page, and densest evidence page remain readable |
| Navigation | every supported forward/backward input consumes internal state before page changes |
| Return state | forward/backward round trip preserves stable geometry and completed/retracted state |
| Focus layout | active timeline/gallery item is geometrically centered after transition |
| Charts | canvas contains rendered pixels; labels, axes, endpoints, and comparisons match the claim |
| Media | images decode, have nonzero dimensions, use intended crops, and work offline |
| Accessibility | controls are reachable, semantics are meaningful, contrast is sufficient, reduced motion is readable |
| Reliability | no console errors; print view shows all essential content; validator reports no undeclared network dependency |

Take screenshots after transitions settle. Measure geometry for transformed layouts; visual memory is not an acceptance test.
