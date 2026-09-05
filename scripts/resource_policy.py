#!/usr/bin/env python3
"""Structured resource auditing shared by the deck builder and validator."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.parse import urlsplit


RESOURCE_ATTRIBUTES = {
    "src",
    "href",
    "xlink:href",
    "poster",
    "data",
    "action",
    "formaction",
}
VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}
REMOTE_RE = re.compile(r"^(?:https?:)?//", re.IGNORECASE)
UNSAFE_SCHEMES = {"blob", "file", "javascript", "vbscript"}
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE | re.DOTALL)
CSS_IMPORT_RE = re.compile(r"@\s*import\b", re.IGNORECASE)
DATA_SRCSET_RE = re.compile(
    r"data:[^,\s]+,[A-Za-z0-9+/=%_-]+(?:\s+\d+(?:\.\d+)?[wx])?",
    re.IGNORECASE,
)


class ResourcePolicyError(ValueError):
    pass


@dataclass
class AuditResult:
    network_iframes: int = 0
    shared_keys: tuple[str, ...] = ()


@dataclass
class _Node:
    tag: str
    attrs: dict[str, str]
    parent: "_Node | None" = None
    children: list["_Node"] = field(default_factory=list)
    text: list[str] = field(default_factory=list)


class _TreeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("#document", {})
        self.stack = [self.root]

    def _add_node(self, tag: str, attrs: list[tuple[str, str | None]], push: bool) -> None:
        normalized = {
            name.lower(): _decode(value or "")
            for name, value in attrs
            if name
        }
        node = _Node(tag.lower(), normalized, self.stack[-1])
        self.stack[-1].children.append(node)
        if push and node.tag not in VOID_ELEMENTS:
            self.stack.append(node)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._add_node(tag, attrs, True)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._add_node(tag, attrs, False)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == lowered:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].text.append(data)


def _decode(value: str) -> str:
    decoded = value
    for _ in range(3):
        expanded = html.unescape(decoded)
        if expanded == decoded:
            break
        decoded = expanded
    return decoded


def _normalized_url(value: str) -> str:
    return "".join(character for character in _decode(value).strip() if ord(character) > 0x20)


def _is_truthy(value: str | None) -> bool:
    return _decode(value or "").strip().lower() in {"1", "true"}


def _classes(node: _Node) -> set[str]:
    return set(node.attrs.get("class", "").split())


def _walk(node: _Node):
    for child in node.children:
        yield child
        yield from _walk(child)


def _contains_fallback(node: _Node) -> bool:
    return "embed-fallback" in _classes(node) or any(
        "embed-fallback" in _classes(descendant) for descendant in _walk(node)
    )


def _network_container(frame: _Node) -> _Node | None:
    candidate: _Node | None = frame
    while candidate is not None:
        if _is_truthy(candidate.attrs.get("data-network-required")):
            return candidate
        candidate = candidate.parent
    return None


def _url_kind(value: str) -> str:
    normalized = _normalized_url(value)
    lowered = normalized.lower()
    if not normalized:
        return "empty"
    if lowered.startswith("asset:"):
        return "asset"
    if lowered.startswith("data:"):
        return "data"
    if normalized.startswith("#"):
        return "fragment"
    if REMOTE_RE.match(normalized):
        return "remote"
    scheme = urlsplit(normalized).scheme.lower()
    if scheme in UNSAFE_SCHEMES:
        return "unsafe"
    if scheme:
        return "scheme"
    return "relative"


def _audit_resource_url(value: str, context: str, *, allow_asset: bool) -> None:
    kind = _url_kind(value)
    if kind in {"data", "fragment", "empty"}:
        return
    if kind == "asset" and allow_asset:
        return
    if kind == "asset":
        raise ResourcePolicyError(f"{context} contains an unresolved asset: URL.")
    if kind == "remote":
        media = any(token in context for token in ("<img", "<audio", "<video", "<source"))
        label = "remote media" if media else "a remote runtime dependency"
        raise ResourcePolicyError(f"{context} uses {label}; embed it locally.")
    if kind == "unsafe":
        raise ResourcePolicyError(f"{context} uses an unsafe URL scheme.")
    raise ResourcePolicyError(f"{context} uses a relative or unsupported runtime dependency; embed it locally.")


def audit_css(css: str, context: str, *, allow_asset: bool) -> None:
    decoded = _decode(css)
    without_comments = re.sub(r"/\*.*?\*/", "", decoded, flags=re.DOTALL)
    if CSS_IMPORT_RE.search(without_comments):
        raise ResourcePolicyError(f"{context} uses CSS @import; inline the stylesheet instead.")
    for match in CSS_URL_RE.finditer(without_comments):
        _audit_resource_url(match.group(2), f"{context} CSS url()", allow_asset=allow_asset)


def _audit_srcset(value: str, context: str, *, allow_asset: bool) -> None:
    decoded = _decode(value).strip()
    if not decoded:
        return
    remainder = DATA_SRCSET_RE.sub("", decoded)
    for candidate in remainder.split(","):
        token = candidate.strip().split(maxsplit=1)[0] if candidate.strip() else ""
        if token:
            _audit_resource_url(token, context, allow_asset=allow_asset)


def audit_html(
    source: str,
    context: str = "HTML",
    *,
    allow_asset: bool = False,
    enforce_unique_shared: bool = False,
) -> AuditResult:
    parser = _TreeParser()
    try:
        parser.feed(source)
        parser.close()
    except (TypeError, ValueError) as exc:
        raise ResourcePolicyError(f"{context} could not be parsed: {exc}") from exc

    shared_keys: list[str] = []
    network_iframes = 0
    for node in _walk(parser.root):
        shared = node.attrs.get("data-shared", "").strip()
        if shared:
            if enforce_unique_shared and shared in shared_keys:
                raise ResourcePolicyError(f"{context} has duplicate data-shared key: {shared}")
            shared_keys.append(shared)

        if "style" in node.attrs:
            audit_css(node.attrs["style"], f"{context} <{node.tag}> style", allow_asset=allow_asset)
        if node.tag == "style":
            audit_css("".join(node.text), f"{context} <style>", allow_asset=allow_asset)

        srcdoc = node.attrs.get("srcdoc")
        if node.tag == "iframe" and srcdoc:
            nested = audit_html(
                srcdoc,
                f"{context} iframe srcdoc",
                allow_asset=allow_asset,
                enforce_unique_shared=False,
            )
            network_iframes += nested.network_iframes

        if "srcset" in node.attrs:
            _audit_srcset(node.attrs["srcset"], f"{context} <{node.tag}> srcset", allow_asset=allow_asset)

        for attribute in RESOURCE_ATTRIBUTES:
            if attribute not in node.attrs:
                continue
            value = node.attrs[attribute]
            if node.tag == "a" and attribute == "href":
                if _url_kind(value) == "unsafe":
                    raise ResourcePolicyError(f"{context} <a> uses an unsafe URL scheme.")
                continue
            if node.tag == "iframe" and attribute == "src" and _url_kind(value) == "remote":
                container = _network_container(node)
                if container is None or not _contains_fallback(container):
                    raise ResourcePolicyError(
                        f"{context} contains a remote iframe without "
                        'data-network-required="true" and an embed-fallback element.'
                    )
                network_iframes += 1
                continue
            _audit_resource_url(value, f"{context} <{node.tag}> {attribute}", allow_asset=allow_asset)

    return AuditResult(network_iframes=network_iframes, shared_keys=tuple(shared_keys))
