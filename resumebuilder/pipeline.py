"""Full pipeline: read YAML → validate → generate Typst → compile PDF."""

import pathlib
import sys

from resumebuilder.renderer.compiler import CompileError, compile_typst
from resumebuilder.renderer.typst_renderer import generate_typst
from resumebuilder.schema import ReadError, read_yaml
from resumebuilder.schema.models import Validate


def build_resume(content_path: str, out_path: str = "resume_draft.pdf"):
    """Render a resume YAML file to a one-page PDF via Typst.

    Args:
        content_path: Path to YAML content file.
        out_path: Output PDF path (default: resume_draft.pdf).
    """
    try:
        raw = read_yaml(pathlib.Path(content_path))
    except ReadError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    try:
        data = Validate.validate_python(raw)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    typst_source = generate_typst(data.model_dump())

    try:
        compile_typst(typst_source, out_path)
    except CompileError as e:
        print(f"ERROR: Typst compilation failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: rendered {out_path}")
