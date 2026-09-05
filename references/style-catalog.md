# Style Catalog

Use this catalog only when choosing or implementing a visual direction. Start from the viewing situation in [content-architecture.md](content-architecture.md), not from a favorite template. If the user has not selected a style, shortlist three that suit the subject and genuinely differ in family, typography, composition, palette, and motion. Expand to at most six only when the user requests wider exploration. Recommend one, but wait for the user's choice unless the user delegates the decision. Do not dump the entire catalog unless asked.

Launch-event styling is not the premium version of every deck. It is appropriate for staged reveals, flagship objects, milestone stories, and high-impact claims. A parent meeting, medical report, research briefing, classroom lesson, operating review, or photo reference guide may instead need a human, editorial, technical, playful, or information-design family. “Polished,” “modern,” and “high-end” do not automatically select a dark background.

All styles use system font fallbacks by default so the output remains self-contained. Embed a licensed font as a data URI only when it materially improves the result.

## Visual Families

- **Editorial narrative:** type, image, caption, annotation, and negative space form a reading sequence rather than a UI surface.
- **Information design:** grids, direct labels, comparisons, and evidence marks lead; grouping exists only where the data requires it.
- **Cinematic/object-led:** one subject or statement controls the frame; secondary copy stays restrained.
- **Product/system:** real interfaces, flows, and system diagrams lead; decorative browser chrome and generic technology styling do not.
- **Expressive/educational:** bolder geometry or color supports participation and explanation without becoming ornamental noise.

## Shortlisting by Situation

Build a varied shortlist rather than offering three shades of one answer:

| Situation | Strong candidates | Usually avoid |
|---|---|---|
| Executive status, operating plan | Boardroom Clarity, Atlas Editorial, Data Observatory | slogan-heavy keynote pacing |
| Research, policy, culture | Atlas Editorial, Field Notes, Museum Minimal | generic dashboards |
| Education, family, community | Warm Human, Playful Geometry, Field Notes | default black/orange launch styling |
| Engineering, medicine, systems | Science Blueprint, Boardroom Clarity, Product Studio | decorative circuitry and unsupported precision |
| Product demonstration | Product Studio, Signal Noir, Boardroom Clarity | fake browser frames that obscure the product |
| Flagship launch or milestone reveal | Flagship Keynote, Signal Noir, Mono Cinema | dense reference-sheet layouts |
| Youth workshop or creative provocation | Playful Geometry, Neo Brutal, Atlas Editorial | muted corporate sameness |
| Art, architecture, premium portfolio | Museum Minimal, Mono Cinema, Atlas Editorial | card grids and dashboard chrome |

At least two shortlisted options should differ in light/dark treatment when both are plausible. At least two should differ in composition family. Do not recommend Flagship Keynote unless the content and delivery actually benefit from staged focus.

## Quick Selection

| ID | Name | Family | Best for | Palette |
|---|---|---|---|---|
| `atlas-editorial` | Atlas Editorial | editorial narrative | strategy, research, cultural narratives | `#F4F1E9` `#17202A` `#D4422F` `#176B87` |
| `signal-noir` | Signal Noir | cinematic/object-led | launches, keynotes, bold product stories | `#090B0E` `#F5F7FA` `#FF614D` `#52D3B2` |
| `flagship-keynote` | Flagship Keynote | cinematic/object-led | premium launches, milestone stories, executive reveals | `#020203` `#F5F5F7` `#FF6B35` `#77777D` |
| `boardroom-clarity` | Boardroom Clarity | information design | executive updates, consulting, plans | `#F5F7F8` `#18212A` `#1769AA` `#DD5842` |
| `data-observatory` | Data Observatory | information design | analytics, dashboards, market evidence | `#10131A` `#EDF2F7` `#00C2A8` `#FFCB47` |
| `field-notes` | Field Notes | editorial narrative | case studies, sustainability, education | `#F0EEE6` `#252B27` `#28765C` `#BE4F3B` |
| `neo-brutal` | Neo Brutal | expressive/educational | provocations, creative pitches, youth culture | `#FFEF5A` `#111111` `#EF3E23` `#1A65FF` |
| `product-studio` | Product Studio | product/system | SaaS demos, roadmaps, feature narratives | `#F7F8FA` `#171A21` `#635BFF` `#00A884` |
| `science-blueprint` | Science Blueprint | product/system | engineering, medicine, technical systems | `#EAF4F8` `#123040` `#0079A8` `#E94F37` |
| `warm-human` | Warm Human | editorial narrative | people stories, brand values, community | `#F8EEE5` `#2D2523` `#D14B3A` `#2E7D73` |
| `museum-minimal` | Museum Minimal | cinematic/object-led | art, architecture, premium portfolios | `#F3F2EF` `#171717` `#B52F2F` `#315F75` |
| `playful-geometry` | Playful Geometry | expressive/educational | workshops, education, creative teams | `#FFF7DF` `#20232A` `#ED4C67` `#167D78` |
| `mono-cinema` | Mono Cinema | cinematic/object-led | documentary, manifesto, founder narrative | `#070707` `#F1F1ED` `#D95445` `#484848` |

## Direction Details

### Atlas Editorial

- Composition: strong columns, generous margins, captions, rules, asymmetric image crops.
- Type: serif display with neutral sans-serif body.
- Motion: measured horizontal page turn; captions and rules reveal after the main statement.
- Charts: sparse axes, direct labels, red only for the argument's decisive signal.
- Avoid: glossy cards, floating decoration, large icon collections.

### Signal Noir

- Composition: full-stage statements, crisp grids, high-contrast media, occasional edge-to-edge charts.
- Type: heavy geometric sans-serif with compact support copy.
- Motion: object continuity, controlled scale, short luminous accents without ambient glow blobs.
- Charts: near-black canvas, coral primary series, mint comparison series.
- Avoid: all-blue technology styling, low-contrast gray text, constant looping effects.

### Flagship Keynote

- Composition: nearly invisible stage chrome, full-frame claims, centered focal objects, and evidence presented without card containers.
- Type: large silver-white display text with quiet gray support copy; one warm accent marks the active word, year, or progress state.
- Motion: one cinematic focus mechanism per page; use scale, blur, opacity, and horizontal travel to direct attention rather than decorate.
- Timelines: keep the active milestone exactly centered and full-size; shrink and fade adjacent milestones by distance; use year labels without a mandatory axis line.
- Avoid: treating black plus orange as a complete style, visible grids, boxed page counters, persistent toolbars, ornamental circles, repeated split layouts, and glowing background blobs.
- Implementation: read [launch-event-style.md](launch-event-style.md) before building this direction.

### Boardroom Clarity

- Composition: title band, evidence-first grids, clean comparisons, restrained KPI grouping.
- Type: compact sans-serif hierarchy optimized for scanning.
- Motion: fast and quiet; emphasize changed values rather than moving every object.
- Charts: white plot area, blue primary, coral exception, direct annotations.
- Avoid: oversized slogans, decorative cards, marketing hero composition.

### Data Observatory

- Composition: dense but organized analytical surfaces with one focal visualization per page.
- Type: tabular numerals, short labels, medium-weight headings.
- Motion: chart build, scrubbed timeline, local focus enlargement.
- Charts: dark plot, mint/yellow/coral categorical separation, visible baselines.
- Avoid: dashboards nested inside panels, too many simultaneous chart types.

### Field Notes

- Composition: documentary image, annotation marks, pull quote, evidence strip.
- Type: humanist serif heading and calm sans-serif body.
- Motion: paper-like lateral reveal without fake page-curl effects.
- Charts: forest green, brick exceptions, minimal gridlines.
- Avoid: distressed textures that damage legibility, sepia monotony.

### Neo Brutal

- Composition: hard borders, offset blocks, oversized labels, purposeful collisions that never obscure content.
- Type: heavy sans-serif, compact all-caps labels.
- Motion: direct snap with short overshoot; no elastic loops.
- Charts: black axes, saturated flat fills, thick strokes.
- Avoid: rounded pills, soft shadows, pastel-only palette.

### Product Studio

- Composition: product surface first, supporting text second; feature states share position across pages.
- Type: modern sans-serif, medium density.
- Motion: shared UI objects, state morphs, short vertical reveals.
- Charts: clear product-color mapping with neutral scaffolding.
- Avoid: fake browser chrome that overwhelms the actual product, purple-only palette.

### Science Blueprint

- Composition: labeled systems, sectional diagrams, evidence and method separated clearly.
- Type: precise sans-serif with optional monospaced annotations.
- Motion: trace flow direction, focus one subsystem at a time.
- Charts: cyan-blue primary, red anomaly, confidence bands where relevant.
- Avoid: decorative circuitry, unsupported precision, tiny labels.

### Warm Human

- Composition: human image or quote leads; data supports rather than dominates.
- Type: serif display, open sans-serif body.
- Motion: calm fades and meaningful object continuity.
- Charts: warm red primary, teal comparison, soft neutral axes.
- Avoid: beige-only composition, stock-like dark overlays, sentimental ornament.

### Museum Minimal

- Composition: one object, one claim, generous negative space, precise captioning.
- Type: editorial serif with small sans-serif metadata.
- Motion: slow object relocation and crop change; minimal secondary animation.
- Charts: only when necessary, reduced to essential marks.
- Avoid: card grids, gradients, decorative icon rows.

### Playful Geometry

- Composition: modular shapes, bold diagrams, energetic but stable grid.
- Type: friendly sans-serif with clear weight changes.
- Motion: short directional entrances and shape continuity.
- Charts: distinct categorical colors with outlines for accessibility.
- Avoid: childish stickers, uncontrolled rainbow palettes, bouncing loops.

### Mono Cinema

- Composition: photographic or typographic full-stage frames, chapter cards, documentary captions.
- Type: serif display with narrow metadata.
- Motion: cuts, restrained cross-dissolves, shared subject crops.
- Charts: monochrome with one red editorial signal.
- Avoid: unreadable text over dark images, film-grain animation, mood without evidence.

## Style Choice Format

When asking the user, use this compact pattern for three choices:

```text
1. Signal Noir - high-contrast keynote; best for product launches.
   #090B0E  #F5F7FA  #FF614D  #52D3B2
```

The names and swatches are part of the choice. Add one sentence recommending a specific option and why. Explain the visible character in ordinary language; do not require the user to know design terminology.

## Composition Gate

Before laying out a page, use the role map in `content-architecture.md`. Choose a composition that makes that role legible. Reuse the deck's grid, type, palette, and motion language, but do not repeat one page skeleton throughout.

Do not use these as automatic defaults:

- a decorative vertical rule beside copy paired with a detached rectangle;
- three equal cards when the facts do not have equal semantic weight;
- a panel behind text merely to occupy space;
- gradients, glowing blobs, generic shapes, or fake browser frames without explanatory value;
- a 50/50 split on most pages;
- oversized claims that visually bury the evidence;
- dark dashboard styling as shorthand for AI or technology.

Cards and panels remain valid for repeated records, comparisons, framed tools, and genuinely grouped information. Their presence must be explained by content structure, not by a need to decorate empty space.
