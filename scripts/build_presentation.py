#!/usr/bin/env python3
"""Build a portable, single-file HTML presentation from a JSON specification."""

from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import re
import sys
from pathlib import Path
from typing import Any

from resource_policy import ResourcePolicyError, audit_css, audit_html


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = SKILL_ROOT / "assets" / "presentation-template.html"
ECHARTS_PATH = SKILL_ROOT / "assets" / "vendor" / "echarts.min.js"
QUOTED_ASSET_PATTERN = re.compile(r"([\"'])asset:([^\"']+)\1")
BARE_ASSET_PATTERN = re.compile(r"asset:([^\s\"'<>)}\],;]+)")
TEMPLATE_MARKERS = (
    "__LANG__",
    "__DECK_TITLE__",
    "__THEME__",
    "__CUSTOM_CSS__",
    "__SLIDES_HTML__",
    "__DECK_SPEC__",
    "__ECHARTS_JS__",
)
THEMES = {
    "atlas-editorial", "signal-noir", "boardroom-clarity", "data-observatory",
    "field-notes", "neo-brutal", "product-studio", "science-blueprint",
    "warm-human", "museum-minimal", "playful-geometry", "mono-cinema",
    "flagship-keynote",
}
DEFAULT_THEME = "boardroom-clarity"
LANGUAGE_PATTERN = re.compile(
    r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$"
)


class BuildError(ValueError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise BuildError(f"Required file not found: {path}") from exc


def data_uri(path: Path) -> str:
    if not path.is_file():
        raise BuildError(f"Asset not found: {path}")
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def embed_asset_tokens(value: Any, base_dir: Path) -> Any:
    if isinstance(value, dict):
        return {key: embed_asset_tokens(item, base_dir) for key, item in value.items()}
    if isinstance(value, list):
        return [embed_asset_tokens(item, base_dir) for item in value]
    if not isinstance(value, str) or "asset:" not in value:
        return value

    def resolve(raw: str) -> str:
        asset_path = (base_dir / raw).resolve()
        try:
            asset_path.relative_to(base_dir.resolve())
        except ValueError as exc:
            raise BuildError(f"Asset path escapes the specification directory: {raw}") from exc
        return data_uri(asset_path)

    def replace_quoted(match: re.Match[str]) -> str:
        quote = match.group(1)
        return f"{quote}{resolve(match.group(2))}{quote}"

    value = QUOTED_ASSET_PATTERN.sub(replace_quoted, value)
    return BARE_ASSET_PATTERN.sub(lambda match: resolve(match.group(1)), value)


def validate_content_policy(content: str, slide_id: str, *, allow_asset: bool) -> None:
    try:
        audit_html(
            content,
            f"Slide '{slide_id}'",
            allow_asset=allow_asset,
            enforce_unique_shared=True,
        )
    except ResourcePolicyError as exc:
        raise BuildError(str(exc)) from exc


def validate_spec(spec: dict[str, Any]) -> None:
    if not isinstance(spec, dict):
        raise BuildError("The deck specification must be a JSON object.")
    meta = spec.get("meta")
    slides = spec.get("slides")
    if not isinstance(meta, dict):
        raise BuildError("meta must be an object.")
    if not isinstance(meta.get("title"), str) or not meta["title"].strip():
        raise BuildError("meta.title must be a non-empty string.")
    language = meta.get("language", "zh-CN")
    if not isinstance(language, str) or not LANGUAGE_PATTERN.fullmatch(language):
        raise BuildError("meta.language must be a valid BCP 47 language tag.")
    theme = meta.get("theme", DEFAULT_THEME)
    if not isinstance(theme, str) or theme not in THEMES:
        raise BuildError(f"meta.theme must be one of: {', '.join(sorted(THEMES))}.")
    aspect_ratio = meta.get("aspectRatio", "16:9")
    if aspect_ratio != "16:9":
        raise BuildError("meta.aspectRatio must be 16:9 for the supplied runtime.")
    custom_css = meta.get("customCss", "")
    if not isinstance(custom_css, str):
        raise BuildError("meta.customCss must be a string when provided.")
    try:
        audit_css(custom_css, "meta.customCss", allow_asset="asset:" in custom_css)
    except ResourcePolicyError as exc:
        raise BuildError(str(exc)) from exc
    if not isinstance(slides, list) or not slides:
        raise BuildError("slides must be a non-empty array.")

    seen_ids: set[str] = set()
    for index, slide in enumerate(slides):
        if not isinstance(slide, dict):
            raise BuildError(f"Slide {index + 1} must be an object.")
        slide_id = slide.get("id")
        content = slide.get("content")
        if not isinstance(slide_id, str) or not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]*", slide_id):
            raise BuildError(f"Slide {index + 1} has an invalid id: {slide_id!r}")
        if slide_id in seen_ids:
            raise BuildError(f"Duplicate slide id: {slide_id}")
        seen_ids.add(slide_id)
        if not isinstance(content, str):
            raise BuildError(f"Slide '{slide_id}' content must be an HTML string.")
        validate_content_policy(content, slide_id, allow_asset="asset:" in content)


def render_slides(slides: list[dict[str, Any]]) -> str:
    rendered: list[str] = []
    for index, slide in enumerate(slides):
        title = str(slide.get("title") or f"Slide {index + 1}")
        classes = "slide is-active" if index == 0 else "slide"
        if slide.get("className"):
            safe_classes = " ".join(
                token for token in str(slide["className"]).split() if re.fullmatch(r"[a-zA-Z0-9_-]+", token)
            )
            if safe_classes:
                classes += f" {safe_classes}"
        notes = slide.get("notes")
        notes_html = ""
        if isinstance(notes, str) and notes.strip():
            notes_html = f'<aside class="speaker-notes" data-notes>{html.escape(notes)}</aside>'
        rendered.append(
            f'<section class="{classes}" id="slide-{html.escape(slide["id"], quote=True)}" '
            f'data-slide-index="{index}" aria-label="{html.escape(title, quote=True)}" '
            f'aria-hidden="{"false" if index == 0 else "true"}">'
            f'<div class="slide-inner">{slide["content"]}</div>{notes_html}</section>'
        )
    return "\n".join(rendered)


def json_for_script(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def replace_once(source: str, marker: str, value: str) -> str:
    count = source.count(marker)
    if count != 1:
        raise BuildError(f"Template marker {marker} must occur exactly once; found {count}.")
    return source.replace(marker, value, 1)


def build(spec_path: Path, output_path: Path) -> Path:
    spec_path = spec_path.resolve()
    try:
        spec = json.loads(read_text(spec_path))
    except json.JSONDecodeError as exc:
        raise BuildError(f"Invalid JSON in {spec_path}: {exc}") from exc
    validate_spec(spec)
    spec = embed_asset_tokens(spec, spec_path.parent)
    validate_spec(spec)

    meta = spec["meta"]
    template = read_text(TEMPLATE_PATH)
    echarts_js = read_text(ECHARTS_PATH).replace("</script", "<\\/script")
    replacements = {
        "__LANG__": html.escape(str(meta.get("language", "zh-CN")), quote=True),
        "__DECK_TITLE__": html.escape(str(meta["title"])),
        "__THEME__": html.escape(str(meta.get("theme", DEFAULT_THEME)), quote=True),
        "__CUSTOM_CSS__": str(meta.get("customCss", "")),
        "__SLIDES_HTML__": render_slides(spec["slides"]),
        "__DECK_SPEC__": json_for_script(spec),
        "__ECHARTS_JS__": echarts_js,
    }
    output = template
    for marker, value in replacements.items():
        output = replace_once(output, marker, value)
    unresolved = [marker for marker in TEMPLATE_MARKERS if marker in output]
    if unresolved:
        raise BuildError(f"Unresolved template markers: {', '.join(sorted(set(unresolved)))}")

    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8", newline="\n")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="Path to the JSON deck specification")
    parser.add_argument("--out", required=True, type=Path, help="Output HTML file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        output = build(args.spec, args.out)
    except (BuildError, OSError) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1
    print(f"Built single-file presentation: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
