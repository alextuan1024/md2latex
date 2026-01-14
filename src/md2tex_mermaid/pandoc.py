from __future__ import annotations

import json
from pathlib import Path

from .util import run_command


def pandoc_markdown_to_json(markdown_text: str, pandoc_path: str, verbose: bool) -> dict:
    cmd = [pandoc_path, "-f", "markdown", "-t", "json"]
    result = run_command(cmd, input_text=markdown_text)
    if result.returncode != 0:
        message = result.stderr.strip() or "pandoc failed"
        raise RuntimeError(f"pandoc markdown->json error: {message}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("pandoc returned invalid JSON") from exc


def pandoc_json_to_latex(
    doc: dict,
    pandoc_path: str,
    template: Path | None,
    verbose: bool,
) -> str:
    cmd = [pandoc_path, "-f", "json", "-t", "latex"]
    if template:
        cmd.extend(["--template", str(template)])
    result = run_command(cmd, input_text=json.dumps(doc))
    if result.returncode != 0:
        message = result.stderr.strip() or "pandoc failed"
        raise RuntimeError(f"pandoc json->latex error: {message}")
    return result.stdout
