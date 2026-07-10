"""Typst PDF compilation wrapper."""

import os
import pathlib
import shutil
import tempfile

import typst


class CompileError(Exception):
    pass


_PACKAGE_DIR = pathlib.Path(__file__).parent / "resumebuilder_typst"


def compile_typst(source: str, output_path: str):
    """Compile Typst source to PDF via the typst Python bindings.

    Creates a temporary directory alongside the resumebuilder_typst
    package, writes the .typ source there, and compiles. Typst resolves
    relative imports from the source file's directory.

    Args:
        source: Typst markup string.
        output_path: Absolute or relative path for the output PDF.
    """
    work_dir = tempfile.mkdtemp(prefix="resumebuilder_")
    pkg_dest = os.path.join(work_dir, "resumebuilder_typst")
    shutil.copytree(str(_PACKAGE_DIR), pkg_dest)

    src_path = os.path.join(work_dir, "resume.typ")
    with open(src_path, "w", encoding="utf-8") as f:
        f.write(source)

    try:
        typst.compile(src_path, output_path)
    except typst.TypstError as e:
        raise CompileError(str(e)) from e
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
