"""
pdf_compiler.py
Compile a .tex file to PDF bytes.

Strategy (tried in order):
  1. Local pdflatex if available on PATH.
  2. Docker image local/pdflatex (built from web_app/backend/Dockerfile.latex).

Raises RuntimeError if neither is available or compilation fails.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def _run(cmd: list, env=None, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, timeout=timeout, env=env)


def compile_tex_to_pdf(tex_path: str) -> bytes:
    """Return PDF bytes compiled from tex_path."""
    tex = Path(tex_path).resolve()

    if shutil.which("pdflatex"):
        return _compile_local(tex)
    return _compile_docker(tex)


def _compile_local(tex: Path) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        proc = _run([
            "pdflatex",
            "-interaction=nonstopmode",
            "-output-directory", tmp,
            str(tex),
        ])
        pdf_path = Path(tmp) / tex.with_suffix(".pdf").name
        if not pdf_path.exists():
            raise RuntimeError(
                f"pdflatex exited {proc.returncode}.\n"
                + proc.stdout.decode(errors="replace")[-2000:]
            )
        return pdf_path.read_bytes()


_IMAGE = "local/pdflatex"

_DOCKERFILE_CONTENT = """\
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \\
    texlive-latex-base \\
    texlive-latex-extra \\
    texlive-fonts-recommended \\
    && rm -rf /var/lib/apt/lists/*
"""


def _ensure_image() -> None:
    """Build local/pdflatex if it is not already present in the local daemon."""
    check = subprocess.run(["docker", "images", "-q", _IMAGE], capture_output=True)
    if check.stdout.strip():
        return  # image already exists

    print(f"Building Docker image '{_IMAGE}' (first-time setup, ~2 min)...")
    with tempfile.TemporaryDirectory() as tmp:
        dockerfile = Path(tmp) / "Dockerfile"
        dockerfile.write_text(_DOCKERFILE_CONTENT)
        build = subprocess.run(
            ["docker", "build", "-t", _IMAGE, "-f", str(dockerfile), tmp],
        )
    if build.returncode != 0:
        raise RuntimeError(f"Failed to build Docker image '{_IMAGE}'.")


def _compile_docker(tex: Path) -> bytes:
    _ensure_image()

    tex_dir = tex.parent
    env = {**os.environ, "MSYS_NO_PATHCONV": "1"}
    win_dir = _to_docker_path(tex_dir)

    proc = _run([
        "docker", "run", "--rm",
        "-v", f"{win_dir}:/data",
        _IMAGE,
        "pdflatex",
        "-interaction=nonstopmode",
        "-output-directory", "/data",
        f"/data/{tex.name}",
    ], env=env, timeout=120)

    pdf_path = tex_dir / tex.with_suffix(".pdf").name
    if not pdf_path.exists():
        raise RuntimeError(
            "Docker pdflatex failed.\n"
            + proc.stdout.decode(errors="replace")[-2000:]
        )
    return pdf_path.read_bytes()


def _to_docker_path(p: Path) -> str:
    """Convert a path to a form Docker on Windows accepts (forward slashes)."""
    return str(p).replace("\\", "/")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python pdf_compiler.py <path/to/resume.tex>", file=sys.stderr)
        sys.exit(1)
    tex_path = sys.argv[1]
    pdf_bytes = compile_tex_to_pdf(tex_path)
    out = Path(tex_path).with_suffix(".pdf")
    out.write_bytes(pdf_bytes)
    print(f"PDF written to {out}")
