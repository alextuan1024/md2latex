from __future__ import annotations

import hashlib
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from .util import ensure_dir, run_command


class MermaidRenderError(RuntimeError):
    pass


@dataclass
class MermaidRenderer:
    assets_dir: Path
    mmdc_path: str
    image_format: str = "pdf"
    keep_temp: bool = False
    verbose: bool = False
    _hash_map: dict[str, dict[str, Path]] = field(default_factory=dict, init=False)
    _temp_dir: Path | None = field(default=None, init=False)
    _temp_context: tempfile.TemporaryDirectory | None = field(default=None, init=False)
    _temp_counter: int = field(default=0, init=False)

    def __enter__(self) -> "MermaidRenderer":
        if self.keep_temp:
            self._temp_dir = self.assets_dir / "_tmp"
            ensure_dir(self._temp_dir)
        else:
            self._temp_context = tempfile.TemporaryDirectory(prefix="md2tex_mermaid_")
            self._temp_dir = Path(self._temp_context.name)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._temp_context:
            self._temp_context.cleanup()
        self._temp_context = None
        self._temp_dir = None

    def render(self, source: str) -> Path:
        ensure_dir(self.assets_dir)
        base_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]
        by_hash = self._hash_map.setdefault(base_hash, {})
        if source in by_hash:
            self._log(f"Reusing cached Mermaid diagram for hash {base_hash}.")
            return by_hash[source]

        ext = self.image_format.lower()
        counter = 0
        while True:
            candidate = self.assets_dir / f"mermaid_{base_hash}_{counter}.{ext}"
            if candidate not in by_hash.values():
                break
            counter += 1

        if not candidate.exists():
            self._log(f"Rendering Mermaid diagram to {candidate}.")
            try:
                self._render_to_path(source, candidate)
            except MermaidRenderError:
                if ext == "pdf":
                    fallback = candidate.with_suffix(".png")
                    self._log(f"PDF render failed; falling back to {fallback}.")
                    if not fallback.exists():
                        self._render_to_path(source, fallback)
                    candidate = fallback
                else:
                    raise
        else:
            self._log(f"Found cached diagram at {candidate}, skipping render.")

        by_hash[source] = candidate
        return candidate

    def _render_to_path(self, source: str, output_path: Path) -> None:
        if not self._temp_dir:
            raise MermaidRenderError("temporary directory not initialized")
        self._temp_counter += 1
        input_path = self._temp_dir / f"diagram_{self._temp_counter}.mmd"
        input_path.write_text(source, encoding="utf-8")

        cmd = [self.mmdc_path, "-i", str(input_path), "-o", str(output_path)]
        result = run_command(cmd)
        if result.returncode != 0:
            message = result.stderr.strip() or "mmdc failed"
            raise MermaidRenderError(f"mmdc error: {message}")

    def _log(self, message: str) -> None:
        if self.verbose:
            print(message, file=sys.stderr)
