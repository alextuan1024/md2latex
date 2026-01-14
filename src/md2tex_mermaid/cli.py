from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .converter import convert_markdown_file
from .util import resolve_executable


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="md2tex-mermaid",
        description="Convert Markdown with Mermaid diagrams to LaTeX.",
    )
    parser.add_argument("input", type=Path, help="Path to input Markdown file")
    parser.add_argument("-o", "--output", required=True, type=Path, help="Output .tex path")
    parser.add_argument(
        "--assets-dir",
        type=Path,
        default=Path("./assets/mermaid"),
        help="Directory for Mermaid diagram assets",
    )
    parser.add_argument(
        "--image-format",
        choices=["pdf", "png"],
        default="pdf",
        help="Preferred Mermaid render format",
    )
    parser.add_argument("--keep-temp", action="store_true", help="Keep temp files")
    parser.add_argument("--pandoc-path", help="Path to pandoc binary")
    parser.add_argument("--mmdc-path", help="Path to mmdc binary")
    parser.add_argument("--template", type=Path, help="Pandoc LaTeX template")
    parser.add_argument(
        "--top-level-division",
        default="chapter",
        help="Pandoc top-level-division (default: chapter)",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.input.exists():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        return 1
    if args.template and not args.template.exists():
        print(f"Error: template file not found: {args.template}", file=sys.stderr)
        return 1

    try:
        pandoc_path = resolve_executable("pandoc", args.pandoc_path)
        mmdc_path = resolve_executable("mmdc", args.mmdc_path)
        assets_dir = args.assets_dir.resolve()
        output_path = args.output.resolve()
        input_path = args.input.resolve()
        template = args.template.resolve() if args.template else None
        convert_markdown_file(
            input_path=input_path,
            output_path=output_path,
            assets_dir=assets_dir,
            pandoc_path=pandoc_path,
            mmdc_path=mmdc_path,
            image_format=args.image_format,
            keep_temp=args.keep_temp,
            template=template,
            top_level_division=args.top_level_division,
            verbose=args.verbose,
        )
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
