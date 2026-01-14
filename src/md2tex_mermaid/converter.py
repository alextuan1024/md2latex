from __future__ import annotations

from pathlib import Path
from pandocfilters import RawBlock, stringify

from .mermaid import MermaidRenderer
from .pandoc import pandoc_json_to_latex, pandoc_markdown_to_json
from .util import escape_latex, ensure_dir, posix_relpath


def convert_markdown_file(
    input_path: Path,
    output_path: Path,
    assets_dir: Path,
    pandoc_path: str,
    mmdc_path: str,
    image_format: str,
    keep_temp: bool,
    template: Path | None,
    verbose: bool,
) -> None:
    markdown_text = input_path.read_text(encoding="utf-8")
    ensure_dir(output_path.parent)
    latex = convert_markdown_text(
        markdown_text,
        output_path.parent,
        assets_dir,
        pandoc_path,
        mmdc_path,
        image_format,
        keep_temp,
        template,
        verbose,
    )
    output_path.write_text(latex, encoding="utf-8")


def convert_markdown_text(
    markdown_text: str,
    output_dir: Path,
    assets_dir: Path,
    pandoc_path: str,
    mmdc_path: str,
    image_format: str,
    keep_temp: bool,
    template: Path | None,
    verbose: bool,
    renderer: MermaidRenderer | None = None,
) -> str:
    doc = pandoc_markdown_to_json(markdown_text, pandoc_path, verbose)
    if renderer is None:
        with MermaidRenderer(
            assets_dir=assets_dir,
            mmdc_path=mmdc_path,
            image_format=image_format,
            keep_temp=keep_temp,
            verbose=verbose,
        ) as mermaid_renderer:
            doc = transform_document(doc, mermaid_renderer, output_dir)
    else:
        doc = transform_document(doc, renderer, output_dir)
    return pandoc_json_to_latex(doc, pandoc_path, template, verbose)


def transform_document(doc: dict, renderer: MermaidRenderer, output_dir: Path) -> dict:
    blocks = doc.get("blocks", [])
    new_blocks = []
    for block in blocks:
        if is_mermaid_codeblock(block):
            caption = None
            if new_blocks and is_caption_paragraph(new_blocks[-1]):
                caption = extract_caption(new_blocks.pop())
            code = block["c"][1]
            image_path = renderer.render(code)
            rel_path = posix_relpath(image_path, output_dir)
            figure_latex = build_figure_latex(rel_path, caption)
            new_blocks.append(RawBlock("latex", figure_latex))
        else:
            new_blocks.append(block)
    doc["blocks"] = new_blocks
    return doc


def is_mermaid_codeblock(block: dict) -> bool:
    if block.get("t") != "CodeBlock":
        return False
    attrs, _code = block["c"]
    _ident, classes, _kvs = attrs
    return classes == ["mermaid"]


def is_caption_paragraph(block: dict) -> bool:
    if block.get("t") != "Para":
        return False
    text = stringify(block.get("c", [])).strip()
    return text.startswith("Caption:") or text.startswith("Figure:")


def extract_caption(block: dict) -> str | None:
    text = stringify(block.get("c", [])).strip()
    for prefix in ("Caption:", "Figure:"):
        if text.startswith(prefix):
            caption = text[len(prefix) :].strip()
            return caption or None
    return None


def build_figure_latex(path: str, caption: str | None) -> str:
    lines = [
        "\\begin{figure}[htbp]",
        "\\centering",
        f"\\includegraphics[width=0.95\\linewidth]{{{path}}}",
    ]
    if caption:
        lines.append(f"\\caption{{{escape_latex(caption)}}}")
    lines.append("\\end{figure}")
    return "\n".join(lines)
