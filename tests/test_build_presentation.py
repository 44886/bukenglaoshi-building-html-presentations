import base64
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = SKILL_ROOT / "scripts" / "build_presentation.py"
VALIDATE_SCRIPT = SKILL_ROOT / "scripts" / "validate_deck.py"


class PresentationBuilderTests(unittest.TestCase):
    def make_fixture(self, root: Path, *, content: str | None = None) -> Path:
        pixel = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
        )
        (root / "pixel.png").write_bytes(pixel)
        spec = {
            "meta": {
                "title": "Builder Test",
                "language": "zh-CN",
                "theme": "signal-noir",
                "aspectRatio": "16:9",
            },
            "slides": [
                {
                    "id": "opening",
                    "title": "Opening",
                    "content": content
                    or '<h1 data-shared="topic">Builder Test</h1><img src="asset:pixel.png" alt="pixel">',
                },
                {
                    "id": "chart",
                    "title": "Chart",
                    "content": '<div class="chart" data-chart-id="trend"><script type="application/json" class="chart-options">{"xAxis":{"type":"category","data":["A","B"]},"yAxis":{"type":"value"},"series":[{"type":"bar","data":[2,5]}]}</script></div>',
                },
            ],
        }
        spec_path = root / "deck.json"
        spec_path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        return spec_path

    def run_builder(self, spec_path: Path, output: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(BUILD_SCRIPT), str(spec_path), "--out", str(output)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_builds_one_self_contained_html_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            spec = self.make_fixture(root)
            output = root / "deck.html"

            result = self.run_builder(spec, output)

            self.assertEqual(result.returncode, 0, result.stderr)
            html = output.read_text(encoding="utf-8")
            self.assertEqual(html.count('<section class="slide'), 2)
            self.assertIn('<section class="slide is-active"', html)
            self.assertIn("data:image/png;base64,", html)
            self.assertIn("echarts.init", html)
            self.assertIn('id="deck-progress"', html)
            self.assertNotIn("__DECK_SPEC__", html)
            self.assertNotIn("__SLIDES_HTML__", html)
            self.assertNotIn("__ECHARTS_JS__", html)

    def test_every_catalog_theme_is_buildable(self):
        catalog = (SKILL_ROOT / "references" / "style-catalog.md").read_text(encoding="utf-8")
        themes = set(re.findall(r"^\| `([a-z0-9-]+)` \|", catalog, flags=re.MULTILINE))
        self.assertGreaterEqual(len(themes), 10)

        for theme in sorted(themes):
            with self.subTest(theme=theme), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                spec_path = self.make_fixture(root)
                spec = json.loads(spec_path.read_text(encoding="utf-8"))
                spec["meta"]["theme"] = theme
                spec_path.write_text(json.dumps(spec), encoding="utf-8")
                result = self.run_builder(spec_path, root / "deck.html")
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_omitted_theme_uses_neutral_information_design_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            spec_path = self.make_fixture(root)
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            del spec["meta"]["theme"]
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            output = root / "deck.html"

            result = self.run_builder(spec_path, output)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('<body data-theme="boardroom-clarity">', output.read_text(encoding="utf-8"))

    def test_rejects_unmarked_remote_iframe(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            spec = self.make_fixture(root, content='<iframe src="https://example.com"></iframe>')
            result = self.run_builder(spec, root / "deck.html")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("remote iframe", result.stderr.lower())

    def test_allows_declared_remote_iframe_with_fallback(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            content = (
                '<div class="web-embed" data-network-required="true">'
                '<iframe src="https://example.com" title="Example" sandbox="allow-scripts"></iframe>'
                '<p class="embed-fallback">Network connection required.</p></div>'
            )
            spec = self.make_fixture(root, content=content)
            output = root / "deck.html"
            result = self.run_builder(spec, output)
            self.assertEqual(result.returncode, 0, result.stderr)

            validation = subprocess.run(
                [sys.executable, str(VALIDATE_SCRIPT), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(validation.returncode, 0, validation.stderr)
            self.assertIn("network-dependent iframe: 1", validation.stdout.lower())

    def test_missing_asset_fails_with_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            spec = self.make_fixture(root, content='<img src="asset:not-found.png" alt="missing">')
            result = self.run_builder(spec, root / "deck.html")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not-found.png", result.stderr)

    def test_rejects_remote_url_in_custom_css(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            spec_path = self.make_fixture(root)
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            spec["meta"]["customCss"] = "body{background:url(https://example.com/background.png)}"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            result = self.run_builder(spec_path, root / "deck.html")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("customcss", result.stderr.lower())

    def test_embeds_unquoted_css_asset_url(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "deck.woff2").write_bytes(b"test-font")
            spec_path = self.make_fixture(root)
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            spec["meta"]["customCss"] = "@font-face{font-family:Deck;src:url(asset:deck.woff2)}"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            output = root / "deck.html"
            result = self.run_builder(spec_path, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            html = output.read_text(encoding="utf-8")
            self.assertIn("data:font/woff2;base64,", html)
            self.assertNotIn("asset:deck.woff2", html)

    def test_rejects_unquoted_remote_media_url(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            spec = self.make_fixture(root, content="<img src=https://example.com/a.png alt=x>")
            result = self.run_builder(spec, root / "deck.html")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("remote media", result.stderr.lower())

    def test_embeds_quoted_asset_path_with_spaces(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "deck font.woff2").write_bytes(b"space-font")
            spec_path = self.make_fixture(root)
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            spec["meta"]["customCss"] = "@font-face{font-family:Deck;src:url('asset:deck font.woff2')}"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            output = root / "deck.html"
            result = self.run_builder(spec_path, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("data:font/woff2;base64,", output.read_text(encoding="utf-8"))

    def test_rejects_encoded_and_protocol_relative_dependencies(self):
        cases = {
            "protocol-relative script": "<script src=//cdn.example.com/app.js></script>",
            "entity-encoded script": '<script src="https&#58;//cdn.example.com/app.js"></script>',
            "remote srcset": '<img src="asset:pixel.png" srcset="https://cdn.example.com/a.png 2x" alt="x">',
            "css import": '<style>@import "https://cdn.example.com/theme.css";</style>',
            "remote object": '<object data="https://cdn.example.com/report.pdf"></object>',
        }
        for name, content in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                spec = self.make_fixture(root, content=content)
                result = self.run_builder(spec, root / "deck.html")
                self.assertNotEqual(result.returncode, 0, f"{name} was accepted")

    def test_rejects_invalid_metadata(self):
        cases = {
            "theme": "unknown-theme",
            "aspectRatio": "4:3",
            "language": "not a language tag!",
        }
        for field, value in cases.items():
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                spec_path = self.make_fixture(root)
                spec = json.loads(spec_path.read_text(encoding="utf-8"))
                spec["meta"][field] = value
                spec_path.write_text(json.dumps(spec), encoding="utf-8")
                result = self.run_builder(spec_path, root / "deck.html")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(field.lower(), result.stderr.lower())

    def test_rejects_duplicate_shared_key_within_slide(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            content = '<div data-shared="signal">A</div><div data-shared="signal">B</div>'
            spec = self.make_fixture(root, content=content)
            result = self.run_builder(spec, root / "deck.html")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate data-shared", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
