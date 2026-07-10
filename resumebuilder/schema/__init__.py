"""YAML reader with ruamel.yaml, preserves line info for error reporting."""
import pathlib

import ruamel.yaml
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.scanner import RoundTripScanner


class ScannerNoAlias(RoundTripScanner):
    """Treat * as plain text instead of YAML alias syntax (for Markdown bold)."""

    def fetch_alias(self) -> None:
        self.fetch_plain()


_yaml = ruamel.yaml.YAML()
_yaml.Scanner = ScannerNoAlias
_yaml.constructor.yaml_constructors["tag:yaml.org,2002:timestamp"] = (
    lambda loader, node: loader.construct_scalar(node)
)


class ReadError(Exception):
    pass


def read_yaml(file_path_or_contents: pathlib.Path | str) -> CommentedMap:
    if isinstance(file_path_or_contents, pathlib.Path):
        if not file_path_or_contents.exists():
            raise ReadError(f"The input file `{file_path_or_contents}` doesn't exist!")
        accepted = {".yaml", ".yml", ".json", ".json5"}
        if file_path_or_contents.suffix not in accepted:
            raise ReadError(
                f"The input file should have one of these extensions: {accepted}. "
                f"Got: {file_path_or_contents.name}"
            )
        content = file_path_or_contents.read_text(encoding="utf-8")
    else:
        content = file_path_or_contents

    data = _yaml.load(content)
    if data is None:
        raise ReadError("The input file is empty!")
    if isinstance(data, str):
        raise ReadError(
            "Expected a YAML dictionary, got a string. Did you pass raw content "
            "instead of a file path?"
        )
    return data
