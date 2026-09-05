# Component Catalog

These recipes match the supplied runtime. Adapt content and ECharts options, but preserve the classes and data attributes that activate behavior.

Recipes demonstrate behavior, not mandatory page shells. First choose a page role using [content-architecture.md](content-architecture.md). Do not wrap a component in `.panel` unless the information is genuinely grouped or the component is a framed tool.

## Shared Elements

Give the same semantic object the same key on consecutive or nonconsecutive pages:

```html
<!-- Page 1 -->
<div class="signal-node" data-shared="growth-signal">42%</div>

<!-- Page 2 -->
<div class="metric" data-shared="growth-signal"><strong>42%</strong><span>qualified growth</span></div>
```

The runtime uses the View Transitions API when present and measured clone animation otherwise. Do not reuse a key for unrelated objects or more than once on a page.

## Staged Reveals

Default to showing the whole page. Use fragments only when premature visibility would distract from the point being spoken, reveal an answer or conclusion too early, or make a chronology, dialogue, demonstration, or decision sequence harder to follow. Do not fragment a cover, agenda, reference table, checklist, set of parallel facts, or peer comparison merely to create motion.

Run a click-density check before building: count every fragment and presenter-controlled timeline item. For a typical 10-page talk, a handful of staged pages is usually enough. Prefer one meaningful reveal that advances the narrative over four cosmetic reveals that expose adjacent labels one by one. When several elements belong to the same spoken beat, wrap them in one fragment so they reveal together:

Use at most one primary motion mechanism on a page. Three manual steps is the normal ceiling; four or five require a real chronology, dialogue, demonstration, or decision sequence, and more than five should be split across pages. If a chart build, count-up, shared transition, or automatic timeline already carries the page's focus, keep surrounding content static. Automatic motion should run once; reserve timeline autoplay for explicitly unattended playback and never add looping decorative animation.

```html
<div class="fragment">
  <p class="claim">The pattern is consistent across all three cohorts.</p>
  <div class="supporting-evidence">...</div>
</div>
```

```html
<ol class="stack">
  <li class="fragment">First implication</li>
  <li class="fragment">Second implication</li>
  <li class="fragment">Decision</li>
</ol>
```

Fragments are manual presentation steps. A forward key, clicker command, Next button, forward swipe, or downward wheel gesture reveals exactly one pending fragment; only the next forward action changes the page after all fragments are visible. Backward inputs retract one fragment at a time before returning to the previous page. Keep DOM order aligned with the spoken narrative; manual steps never autoplay.

## Count-Up Metrics

```html
<div class="metric">
  <span class="label">Annual recurring revenue</span>
  <strong class="value count-up" data-value="128.4" data-prefix="$" data-suffix="M" data-decimals="1" data-duration="1400">0</strong>
  <span class="context">+31% year over year</span>
</div>
```

Supported fields: `data-value`, `data-prefix`, `data-suffix`, `data-decimals`, and `data-duration` in milliseconds. The locale comes from `meta.language`.

## ECharts

```html
<figure style="min-height:520px">
  <div class="chart" data-chart-id="adoption" data-renderer="canvas">
    <script type="application/json" class="chart-options">
      {
        "animationDuration": 900,
        "tooltip": {"trigger": "axis"},
        "grid": {"left": 56, "right": 24, "top": 30, "bottom": 44},
        "xAxis": {"type": "category", "data": ["Q1", "Q2", "Q3", "Q4"]},
        "yAxis": {"type": "value"},
        "series": [
          {"name": "Adoption", "type": "line", "smooth": true, "symbolSize": 10, "data": [18, 34, 57, 82]}
        ]
      }
    </script>
  </div>
  <figcaption>Adoption by quarter; active customer cohort.</figcaption>
</figure>
```

The runtime vendors ECharts, initializes charts only on active pages, applies theme colors when `option.color` is absent, resizes with the stage, and marks successful containers `.is-ready`.

Recommended chart choices:

| Story | Chart |
|---|---|
| Change over time | line/area |
| Compare categories | horizontal bar |
| Composition | stacked bar; pie only for very few categories |
| Relationship | scatter |
| Flow | sankey |
| Sequence/dependencies | graph or custom HTML process flow |

Use direct annotations and honest axes. Do not use decorative 3D charts.

## Animated Timeline With Local Focus

```html
<div class="timeline" data-autoplay="2200" data-start="0">
  <div class="timeline-track"><div class="timeline-fill"></div></div>
  <div class="timeline-items">
    <article class="timeline-item"><div class="time">Q1</div><h3>Discover</h3><p>Validate the signal.</p></article>
    <article class="timeline-item"><div class="time">Q2</div><h3>Build</h3><p>Ship the core loop.</p></article>
    <article class="timeline-item"><div class="time">Q3</div><h3>Scale</h3><p>Expand distribution.</p></article>
  </div>
</div>
```

The fill advances, the active item enlarges locally, and click/Enter/Space focuses a step and stops autoplay. Omit `data-autoplay` for presenter-controlled timelines: the runtime then treats each `.timeline-item` as a manual presentation step, revealing and focusing one node per forward input. Use `data-autoplay` only when unattended cycling is intentional; automatic timelines do not consume page-navigation steps.

## Embedded Web Content

Offline `srcdoc` is preferred:

```html
<div class="web-embed">
  <span class="embed-status">Embedded</span>
  <iframe title="Local interactive demo" sandbox="allow-scripts"
    srcdoc="<!doctype html><html><body><button onclick='this.textContent=&quot;Complete&quot;'>Run</button></body></html>"></iframe>
  <p class="embed-fallback">The local demo could not load.</p>
</div>
```

A remote iframe must add `data-network-required="true"` to the container and an `.embed-fallback` message. Use the narrowest sandbox permissions that work.

## Images and Media

```html
<figure class="figure">
  <img src="asset:media/research-map.webp" alt="Map showing three research clusters">
  <figcaption>Source: field research, August 2026.</figcaption>
</figure>
```

```html
<video src="asset:media/prototype.mp4" controls preload="metadata" poster="asset:media/poster.jpg"></video>
```

Use meaningful alt text. `data-autoplay` is available, but audience-controlled playback is usually more reliable. Compress media before embedding; Base64 increases binary size by roughly one third.

## Photo and Reference Pages

When the audience may photograph the page, render every required item in its final state immediately. Use a clear title, two to four groups, short line lengths, and strong numbering. Do not attach `.fragment` to checklist items. A subtle page entrance may provide continuity, but the page must be fully understandable in one still image and in print.

Prefer hierarchy over tiny type. Condense wording, combine duplicates, and use labels before shrinking below the base body size. Contact sheets, homework instructions, reading guidance, schedules, and summary checklists are reference pages even when they appear inside a presenter-led talk.

## Presenter-Controlled Focus Gallery

Use a focus gallery when several images must remain visible for context but the presenter discusses one at a time. The first image is current on entry; each later image corresponds to one manual fragment. On every step:

- center the current image from measured geometry;
- enlarge it modestly and keep it crisp;
- reduce adjacent images by distance using scale and opacity;
- keep captions tied to their image;
- recompute state from the current index instead of appending transforms;
- return from the next page in the completed gallery state, then retract one image per backward input.

Do not use a focus gallery when the audience must compare all images at equal weight or photograph them. Use a static grid or contact sheet instead.

## KPI Evidence

```html
<div class="metric-grid">
  <article class="metric"><span class="label">Activation</span><strong class="value count-up" data-value="68" data-suffix="%">0</strong><span class="context">+12 points</span></article>
  <article class="metric"><span class="label">Cycle time</span><strong class="value count-up" data-value="4.2" data-suffix=" days" data-decimals="1">0</strong><span class="context">down from 7.8</span></article>
</div>
```

Use at most four primary KPIs on one page. Include context, baseline, or comparison; a large number alone is not an argument. Equal metric cards are appropriate only when the measures are peers. Otherwise make the decisive metric dominant and place supporting measures in a quieter evidence strip.

## Comparison Table

```html
<table>
  <thead><tr><th>Option</th><th>Time to value</th><th>Risk</th><th>Decision</th></tr></thead>
  <tbody>
    <tr><td>Extend</td><td>2 weeks</td><td>Low</td><td class="accent-2">Recommended</td></tr>
    <tr><td>Replace</td><td>10 weeks</td><td>High</td><td>Hold</td></tr>
  </tbody>
</table>
```

Keep cells scannable. If the table needs paragraphs, split it across pages or use a focused comparison layout.

## Quote and Evidence

```html
<blockquote class="quote">The handoff stopped feeling like a handoff.</blockquote>
<p class="quote-source">Research participant 07, operations lead</p>
```

Quotes require a real source or an explicit placeholder supplied by the user. Never fabricate testimonials.

## Process Flow

```html
<ol class="stack">
  <li class="fragment"><p class="eyebrow">01</p><h3>Detect</h3><p>Surface the exception.</p></li>
  <li class="fragment"><p class="eyebrow">02</p><h3>Decide</h3><p>Route with context.</p></li>
  <li class="fragment"><p class="eyebrow">03</p><h3>Resolve</h3><p>Close the learning loop.</p></li>
</ol>
```

For more complex flows, use inline SVG with accessible labels or an ECharts graph. Do not use external diagram runtimes.

## Accessibility and Density

- Use one `h1` on the opening page and an `h2` for later page titles.
- Keep body copy at the runtime's 25px default or larger; never scale type with viewport width.
- Do not place important controls inside shared elements.
- Ensure contrast remains readable in the selected style and test color meaning without relying on hue alone.
- Avoid nested cards. Use panels only for genuinely grouped tools or repeated items.
- The densest page is the first overflow test. If it clips, reduce content or change layout before shrinking type.
- Presentation clickers usually emulate PageUp/PageDown or arrow keys. The runtime also accepts ArrowUp/ArrowDown, Enter, Space, Backspace, and recognized next/previous media or browser keys when focus is not in an editable control.
