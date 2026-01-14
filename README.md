# md2tex-mermaid

Convert Markdown files that include Mermaid diagrams into LaTeX with image inclusions.

## Requirements

- Python 3.11+
- Pandoc (`pandoc`)
- Mermaid CLI (`mmdc`)

## Install (uv)

```sh
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Usage

```sh
md2tex-mermaid input.md -o output.tex
```

Options:

- `--assets-dir ./assets/mermaid`
- `--image-format pdf|png` (default: pdf)
- `--keep-temp`
- `--pandoc-path /path/to/pandoc`
- `--mmdc-path /path/to/mmdc`
- `--template /path/to/template.tex`
- `--verbose`

## Testing

```sh
uv pip install -e .[test]
pytest
```
