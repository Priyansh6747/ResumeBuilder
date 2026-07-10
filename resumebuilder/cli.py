import argparse
import sys

from resumebuilder.pipeline import build_resume


def main():
    parser = argparse.ArgumentParser(
        prog="resume-builder",
        description="Render a content.json into a one-page resume PDF.",
    )
    parser.add_argument("content", help="Path to content.json")
    parser.add_argument("-o", "--output", default="resume_draft.pdf",
                        help="Output PDF path (default: resume_draft.pdf)")
    args = parser.parse_args()

    try:
        build_resume(args.content, args.output)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
