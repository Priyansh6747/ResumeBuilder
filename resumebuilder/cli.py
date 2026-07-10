"""CLI entry point: resume-builder content.yaml [-o out.pdf]"""

import argparse

from resumebuilder.pipeline import build_resume


def main():
    parser = argparse.ArgumentParser(
        prog="resume-builder",
        description="Render a resume YAML into a one-page PDF via Typst.",
    )
    parser.add_argument("content", help="Path to YAML content file")
    parser.add_argument("-o", "--output", default="resume_draft.pdf",
                        help="Output PDF path (default: resume_draft.pdf)")
    args = parser.parse_args()

    build_resume(args.content, args.output)
