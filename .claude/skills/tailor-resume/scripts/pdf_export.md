# PDF Export

## Automatic (preferred)

```bash
python scripts/pdf_compiler.py out/resume.tex
```

Tries local `pdflatex` first; falls back to the `local/pdflatex` Docker image automatically.
PDF is written alongside the `.tex` file.

## Prerequisites for Docker fallback

Only Docker Desktop is required — the image is built automatically on first use.

## Manual (if Docker is unavailable)

```bash
pdflatex -interaction=nonstopmode -output-directory out out/resume.tex
```

Or upload `resume.tex` to Overleaf (pdfLaTeX compiler).

## Notes

- One compile pass is enough for this template (no cross-references).
- Verify ATS readability by selecting/copying text from the exported PDF.
