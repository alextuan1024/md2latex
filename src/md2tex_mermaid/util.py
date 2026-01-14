from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Sequence


def resolve_executable(name: str, override: str | None) -> str:
    if override:
        path = Path(override)
        if not path.exists():
            raise RuntimeError(f"{name} not found at: {override}")
        return str(path)

    resolved = shutil.which(name)
    if not resolved:
        raise RuntimeError(f"{name} not found in PATH; install it or pass --{name}-path")
    return resolved


def run_command(args: Sequence[str], input_text: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        list(args),
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def posix_relpath(target: Path, base_dir: Path) -> str:
    rel = Path(os.path.relpath(target, base_dir))
    return rel.as_posix()


def escape_latex(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

