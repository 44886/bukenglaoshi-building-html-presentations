# Flagship Keynote Style

Use this reference when the user asks for an Apple-style or Xiaomi-style launch event, a premium keynote, a flagship reveal, or says that a dark presentation still looks like an AI template.

## Core Principle

High-end launch-event design comes from removing presentation software from the frame. A black background and a bright accent are only palette choices. The result feels like a keynote when the stage is quiet, typography carries the claim, real evidence appears without card frames, and one focal motion controls attention.

Do not copy a company's logo, exact product artwork, or proprietary trade dress. Treat Apple and Xiaomi as shorthand for pacing, hierarchy, restraint, and stage presence.

## Choose the Variant

When the user has not already chosen, offer these as genuinely different directions:

| Variant | Character | Palette | Best use |
|---|---|---|---|
| Apple-like restraint | cool, quiet, object-led | `#020203` `#F5F5F7` `#9B9BA1` | premium objects, manifesto claims |
| Xiaomi-like energy | clear, warm, fast | `#050505` `#FFFFFF` `#FF6900` | milestones, technology, energetic reveals |
| Flagship hybrid | restrained stage with warm focus | `#020203` `#F5F5F7` `#FF6B35` `#77777D` | education, people stories, executive keynotes |

Use the user's chosen variant consistently. Do not turn the options into three minor shades of the same layout.

## Stage System

### Remove the template frame

- Suppress the runtime grid on launch slides with `#deck-stage::before { opacity: 0 }`.
- Keep the required progress indicator, but reduce it to a 1-2px hairline with one warm active color.
- Render the page counter as quiet tabular text without a box, border, or blurred panel.
- Keep controls available for accessibility and touch, but let them default to `opacity: 0`; reveal them on `:hover` and `:focus-within`.
- Remove decorative rails, repeated dividers, fake browser frames, ornamental circles, and ambient glow blobs.
- Use near-black tonal depth rather than a flat gray dashboard surface. A restrained vertical tonal shift is enough.

For a deck whose launch style applies only to selected pages, scope the chrome with the active slide:

```css
.slide.launch-slide { background: linear-gradient(180deg, #020203, #09090b 48%, #020203); }
body:has(.launch-slide.is-active) #deck-stage { box-shadow: none; }
body:has(.launch-slide.is-active) #deck-stage::before { opacity: 0; }
body:has(.launch-slide.is-active) #progress-shell { height: 2px; background: rgba(255,255,255,.06); }
body:has(.launch-slide.is-active) #deck-progress { background: #ff6b35; }
body:has(.launch-slide.is-active) #deck-counter { padding: 0; border: 0; background: transparent; }
body:has(.launch-slide.is-active) #controls { opacity: 0; transition: opacity .25s ease; }
body:has(.launch-slide.is-active) #controls:hover,
body:has(.launch-slide.is-active) #controls:focus-within { opacity: 1; }
```

Do not remove the navigation elements from the DOM or make keyboard navigation depend on pointer hover.

## Typography-Led Claim Page

A claim or opening page should usually contain only the exact statement being spoken. If the user asks for only a phrase, do not add an eyebrow, subtitle, logo, circle, illustration, or explanatory copy.

- Give the support line a quiet silver-gray weight.
- Let the decisive line dominate in silver-white; use the warm accent only on one semantic detail such as punctuation or a keyword.
- Place the text at the stage center or 10-30px above it. Override the cover template's bottom alignment instead of compensating with a fragile oversized wrapper.
- Use one entrance: support copy rises from a small offset while the decisive line resolves from slight blur and scale.
- Reset hidden/animated state outside `.is-active` so returning to the page can replay without changing geometry.

Never animate decorative objects on a page whose message is already carried by a single large statement.

## Horizontal Focus Timeline

Use a focus carousel when chronology is spoken one milestone at a time and seeing later milestones early would distract. It is especially effective for a resume, product evolution, or sequence of achievements.

### Composition

- The viewport spans the full stage and masks only the far left and right edges.
- Every event has a stable width. Translate the track so the active event's bounding-box center equals the stage center.
- The active event is `scale(1)`, fully opaque, and unblurred.
- Adjacent events should remain recognizable but secondary: approximately `scale(.74-.82)`, `opacity(.18-.35)`, and `blur(1.5-3px)`.
- Distant events may fall to `scale(.58-.68)`, `opacity(.02-.10)`, and stronger blur.
- Put the year or step number in the warm accent. Keep headings silver-white and support copy neutral gray.
- Show real books, certificates, interfaces, or products directly. Use object-fit, restrained shadow, and at most slight perspective; do not place evidence in decorative cards.
- A bottom row of quiet year labels is sufficient. An axis line and dots are optional, not a definition of a timeline.

### Presenter-controlled state

Create one hidden fragment for each future milestone. Derive the active index from the number of `.is-revealed` fragments and update the track, event distance, `is-current`, year markers, and `aria-hidden` state from that index.

The interaction contract is strict:

1. Entering from the previous page focuses the first milestone with zero fragments revealed.
2. Every forward input reveals one fragment and focuses exactly one later milestone.
3. The page changes only after the last milestone is focused and the presenter advances again.
4. Returning from the next page restores the timeline at its completed state.
5. Every backward input retracts one milestone before the presentation returns to the previous page.

Use this mechanism only for a real chronology. Five internal steps are acceptable for a six-point resume because each click corresponds to a spoken year; a decorative list should not incur that click burden.

## Motion Language

Use one primary mechanism per page:

| Page role | Primary motion | Typical duration |
|---|---|---|
| Claim | focus from blur plus small rise | 700-1100ms |
| Timeline | horizontal track travel plus local scale/fade | 850-1050ms |
| Evidence reveal | object lift or crop change | 650-900ms |

Use a deliberate easing curve such as `cubic-bezier(.16,.82,.2,1)`. Do not loop motion. Under `prefers-reduced-motion: reduce`, remove travel, blur transitions, and long delays while leaving the final state readable.

## Anti-Template Gate

Reject or revise the page when any of these are true:

- It could be described as "black background plus orange text" without mentioning hierarchy or focus.
- The runtime grid, boxed counter, or toolbar is more visible than the content.
- A left rule and a detached right rectangle substitute for composition.
- Empty space is filled with circles, glow blobs, generic lines, or panels.
- Evidence is placed inside a card only to make it look designed.
- Multiple objects animate independently without a narrative reason.
- The active timeline item is visually large but not geometrically centered.

## Browser Acceptance

Verify the result in a real browser, not from source alone:

- At 1440x900, screenshots of the claim page and the densest evidence milestone are nonblank and free of clipping, overlap, and scrollbars.
- Measure `activeCenterX - stageCenterX`; the timeline focal event should be within 1px of center after its transition settles.
- Measure the claim group before leaving and after returning; its center should be unchanged and should remain near the intended vertical target.
- Confirm claim pages contain only requested semantic content and no stray SVG, circles, labels, or support copy.
- Exercise PageDown through every internal milestone; the counter and hash must remain on the same page until the sequence is complete.
- Exercise PageUp from the next page through every reverse step and back to the claim page.
- Confirm every evidence image has nonzero natural dimensions and the console has no errors.
- Verify the controls remain reachable by keyboard or pointer even when visually hidden.
