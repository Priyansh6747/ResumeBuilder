"""Typst PDF compilation wrapper."""

import os
import tempfile

import typst


class CompileError(Exception):
    pass


def compile_typst(source: str, output_path: str):
    """Compile Typst source to PDF via the typst Python bindings.

    Writes the source to a temporary .typ file and compiles it.

    Args:
        source: Typst markup string.
        output_path: Absolute or relative path for the output PDF.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".typ", delete=False, encoding="utf-8") as f:
        f.write(source)
        tmp_path = f.name

    try:
        typst.compile(tmp_path, output_path)
    except typst.TypstError as e:
        raise CompileError(str(e)) from e
    finally:
        os.unlink(tmp_path)
