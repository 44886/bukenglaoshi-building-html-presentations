#!/usr/bin/env python3
"""Validate structural and offline invariants of a generated HTML deck."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from resource_policy import ResourcePolicyError, audit_html


REQUIRED_MARKERS = (
    'id="deck-progress"',
    'id="deck-stage"',
    'id="deck-counter"',
    'id="next-slide"',
    'id="previous-slide"',
    "echarts.init",
    "startViewTransition",
    "data-shared",
)
TEMPLATE_MARKERS = (
    "__LANG__",
    "__DECK_TITLE__",
    "__THEME__",
    "__CUSTOM_CSS__",
    "__SLIDES_HTML__",
    "__DECK_SPEC__",
    "__ECHARTS_JS__",
)
def validate(path: Path) -> tuple[int, int]:
    if not path.is_file():
        raise ValueError(f"HTML file not found: {path}")
    source = path.read_text(encoding="utf-8")
    if len(source) < 10_000:
        raise ValueError("HTML output is unexpectedly small; embedded runtime may be missing.")
    unresolved = [marker for marker in TEMPLATE_MARKERS if marker in source]
    if unresolved:
        raise ValueError(f"Unresolved template markers: {', '.join(sorted(set(unresolved)))}")
    for marker in REQUIRED_MARKERS:
        if marker not in source:
            raise ValueError(f"Required runtime hook missing: {marker}")
    try:
        audit = audit_html(source, "Generated deck", allow_asset=False)
    except ResourcePolicyError as exc:
        raise ValueError(str(exc)) from exc

    slides = len(re.findall(r'<section class="slide(?:\s|\")', source))
    if slides < 1:
        raise ValueError("No slide sections found.")
    return slides, audit.network_iframes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    args = parser.parse_args()
    try:
        slides, network_iframes = validate(args.html)
    except (OSError, ValueError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Validation passed: slides: {slides}; network-dependent iframe: {network_iframes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
