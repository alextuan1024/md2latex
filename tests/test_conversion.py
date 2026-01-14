from __future__ import annotations

from pathlib import Path

import md2tex_mermaid.converter as converter


def sample_doc() -> dict:
    return {
        "pandoc-api-version": [1, 22, 2],
        "meta": {},
        "blocks": [
            {
                "t": "Header",
                "c": [
                    1,
                    ["", [], []],
                    [
                        {"t": "Str", "c": "Sample"},
                        {"t": "Space"},
                        {"t": "Str", "c": "Title"},
                    ],
                ],
            },
            {
                "t": "Para",
                "c": [
                    {"t": "Str", "c": "This"},
                    {"t": "Space"},
                    {"t": "Str", "c": "paragraph"},
                    {"t": "Space"},
                    {"t": "Str", "c": "has"},
                    {"t": "Space"},
                    {"t": "Strong", "c": [{"t": "Str", "c": "bold"}, {"t": "Space"}, {"t": "Str", "c": "text"}]},
                    {"t": "Space"},
                    {"t": "Str", "c": "here."},
                ],
            },
            {
                "t": "Para",
                "c": [
                    {"t": "Str", "c": "Caption:"},
                    {"t": "Space"},
                    {"t": "Str", "c": "First"},
                    {"t": "Space"},
                    {"t": "Str", "c": "diagram"},
                ],
            },
            {
                "t": "CodeBlock",
                "c": [["", ["mermaid"], []], "graph TD\n  A-->B\n"],
            },
            {
                "t": "Para",
                "c": [
                    {"t": "Str", "c": "Figure:"},
                    {"t": "Space"},
                    {"t": "Str", "c": "Second"},
                    {"t": "Space"},
                    {"t": "Str", "c": "diagram"},
                ],
            },
            {
                "t": "CodeBlock",
                "c": [["", ["mermaid"], []], "sequenceDiagram\n  Alice->>Bob: Hello\n"],
            },
        ],
    }


def fake_pandoc_markdown_to_json(markdown_text: str, pandoc_path: str, verbose: bool) -> dict:
    return sample_doc()


def fake_pandoc_json_to_latex(doc: dict, pandoc_path: str, template: Path | None, verbose: bool) -> str:
    def render_inlines(inlines: list[dict]) -> str:
        parts: list[str] = []
        for inline in inlines:
            kind = inline["t"]
            if kind == "Str":
                parts.append(inline["c"])
            elif kind == "Space":
                parts.append(" ")
            elif kind == "Strong":
                parts.append(f"\\textbf{{{render_inlines(inline['c'])}}}")
        return "".join(parts)

    def render_blocks(blocks: list[dict]) -> str:
        lines: list[str] = []
        for block in blocks:
            kind = block["t"]
            if kind == "Header":
                level = block["c"][0]
                title = render_inlines(block["c"][2])
                command = {
                    1: "section",
                    2: "subsection",
                    3: "subsubsection",
                }.get(level, "paragraph")
                lines.append(f"\\{command}{{{title}}}")
            elif kind == "Para":
                lines.append(render_inlines(block["c"]))
            elif kind == "RawBlock":
                lines.append(block["c"][1])
        return "\n\n".join(lines)

    return render_blocks(doc.get("blocks", []))


class FakeRenderer:
    def __init__(self, assets_dir: Path) -> None:
        self.assets_dir = assets_dir
        self.counter = 0

    def render(self, source: str) -> Path:
        self.counter += 1
        path = self.assets_dir / f"mermaid_test_{self.counter}.pdf"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"%PDF-1.4\n")
        return path


def test_mermaid_and_formatting(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(converter, "pandoc_markdown_to_json", fake_pandoc_markdown_to_json)
    monkeypatch.setattr(converter, "pandoc_json_to_latex", fake_pandoc_json_to_latex)

    assets_dir = tmp_path / "assets" / "mermaid"
    renderer = FakeRenderer(assets_dir)

    latex = converter.convert_markdown_text(
        markdown_text="# Sample Title",
        output_dir=tmp_path,
        assets_dir=assets_dir,
        pandoc_path="pandoc",
        mmdc_path="mmdc",
        image_format="pdf",
        keep_temp=False,
        template=None,
        verbose=False,
        renderer=renderer,
    )

    assert "\\includegraphics" in latex
    assert "\\section{Sample Title}" in latex
    assert "\\textbf{bold text}" in latex
