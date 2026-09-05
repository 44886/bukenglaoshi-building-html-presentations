# Deck Specification

The builder consumes UTF-8 JSON. The specification stays beside source assets; the generated HTML is the only runtime deliverable.

## Top-Level Shape

```json
{
  "meta": {
    "title": "Quarterly Product Narrative",
    "language": "zh-CN",
    "theme": "boardroom-clarity",
    "aspectRatio": "16:9",
    "customCss": ".hero-mark { width: 180px; }"
  },
  "slides": []
}
```

### `meta`

| Field | Required | Meaning |
|---|---:|---|
| `title` | yes | Browser title and deck identity |
| `language` | no | BCP 47 language tag; defaults to `zh-CN` |
| `theme` | no | Style ID from `style-catalog.md`; defaults to neutral `boardroom-clarity`. Set it explicitly for authored decks. |
| `aspectRatio` | no | Keep `16:9`; the supplied runtime is 1600 x 900 |
| `customCss` | no | Deck-specific CSS; keep it scoped and self-contained |

## Slide Shape

```json
{
  "id": "market-signal",
  "title": "The signal changed",
  "className": "dashboard",
  "content": "<div class=\"stack\"><p class=\"eyebrow\">Evidence</p><h2 data-shared=\"chapter-title\">The signal changed</h2></div>",
  "notes": "Pause on the second series and explain the seasonal effect."
}
```

| Field | Required | Meaning |
|---|---:|---|
| `id` | yes | Unique HTML-safe identifier beginning with a letter |
| `title` | no | Accessible page label; supply it even when the visual page has no title |
| `className` | no | Space-separated slide layout classes such as `cover`, `split`, `dashboard`, `quote-slide` |
| `content` | yes | Semantic HTML placed inside `.slide-inner` |
| `notes` | no | Plain-text speaker notes, toggled with the S key and hidden in the audience view |

Treat `id` as the stable editing key. Keep it unchanged when the visible title or slide number changes. Insertions, reorders, and deletions should target IDs so rebuilding the same specification cannot duplicate content or apply an edit to the wrong page.

The runtime provides `.stack`, `.row`, `.between`, `.cols-2`, `.cols-3`, `.panel`, `.metric-grid`, `.metric`, `.figure`, `.callout`, `.chips`, and typography utilities. Use a slide-specific class plus `customCss` for layouts that these utilities cannot express.

## Local Assets

Use `asset:` followed by a path relative to the JSON file:

```html
<img src="asset:media/product-screen.png" alt="Product screen showing the review queue">
<video src="asset:media/demo.mp4" controls preload="metadata"></video>
```

The builder replaces every asset token in strings with a Base64 data URI. Quoted paths may contain spaces; bare paths end at CSS or HTML delimiters. Missing files and paths escaping the specification directory fail the build. It resolves common image, audio, video, font, and document MIME types with `mimetypes`.

For a custom font, place the file locally and add:

```json
{
  "customCss": "@font-face{font-family:DeckSans;src:url(asset:fonts/deck.woff2) format('woff2');font-display:swap} :root{--font-body:DeckSans,Arial,sans-serif}"
}
```

## Content Rules

- Use real headings, lists, figures, tables, and quotes. Do not build all text from anonymous `div` elements.
- Keep one main claim per page and one focal visual hierarchy.
- Preserve approved wording and source facts in the JSON. Do not treat generated HTML as the editable source of truth.
- Use `data-shared` only for the same semantic object across pages. Keys must be unique within one page.
- Keep chart options in `<script type="application/json" class="chart-options">`; JSON cannot contain JavaScript functions.
- Escape quotes correctly inside JSON strings. For complex decks, generate the JSON with a structured serializer rather than hand-concatenating strings.
- Do not place untrusted raw HTML into `content`. The builder packages authored presentation content; it is not an HTML sanitizer.

## Network Policy

Remote and relative runtime dependencies are rejected, including protocol-relative URLs, encoded schemes, `srcset`, object data, CSS `@import`, and CSS `url()`. Normal anchor links are allowed; unsafe anchor schemes are not. The same structured policy audits source content and the generated HTML.

For an offline web demo, use `srcdoc`:

```html
<div class="web-embed">
  <iframe title="Offline calculator" sandbox="allow-scripts"
    srcdoc="<!doctype html><html><body><button>Run</button></body></html>"></iframe>
  <p class="embed-fallback">The embedded demo could not be displayed.</p>
</div>
```

For a genuinely remote page, the enclosing content must include both the marker and fallback:

```html
<div class="web-embed" data-network-required="true">
  <iframe src="https://example.com/demo" title="Live demo" sandbox="allow-scripts allow-forms"></iframe>
  <p class="embed-fallback">Open the live demo in a networked browser.</p>
</div>
```

Remote sites may block embedding through CSP or `X-Frame-Options`. The fallback remains visible as a conservative network notice because an iframe `load` event does not prove that the intended page rendered. Test the real URL; never imply that the outer HTML can override those headers.

## Build Commands

```powershell
python <skill-dir>/scripts/build_presentation.py deck.json --out presentation.html
python <skill-dir>/scripts/validate_deck.py presentation.html
```

The first command packages the deck; the second audits the generated artifact. Both must exit with code 0.

When maintaining the Skill itself:

```powershell
python -m unittest discover -s tests -v
cd tests/browser
npm install
npm test
```

The Playwright suite uses a temporary build and leaves the example source unchanged.
