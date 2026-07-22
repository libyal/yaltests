#!/usr/bin/env python3
"""Writes a CLI tool stat reference file."""

import argparse
import json
import os
import sys


class CliToolStatWriter:
    """Writes a CLI tool stat reference file."""

    _ATTRIBUTE_NAMES = frozenset(
        [
            "access_time",
            "change_time",
            "creation_time",
            "file_mode",
            "group_identifier",
            "inode_number",
            "modification_time",
            "number_of_links",
            "size",
            "user_identifier",
        ]
    )

    def get_reference_format(self, output_file_object: IO) -> dict:
        """Converts (normalized) JSON output of CLI tool output into reference format.

        Args:
          output_file_object (file): file-like object containing the normalized JSON
              output of CLI tool output.

        Returns:
          dict[str, str]: results in reference format.
        """
        file_data = output_file_object.read()
        output_dict = json.loads(file_data)

        return {
            attribute_name: output_dict[attribute_name]
            for attribute_name in self._ATTRIBUTE_NAMES
            if attribute_name in output_dict
        }


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(
        description="Writes a CLI tool stat output reference file."
    )
    argument_parser.add_argument(
        "reference_file",
        nargs="?",
        action="store",
        metavar="PATH",
        default=None,
        help="path of the reference file file.",
    )
    options = argument_parser.parse_args()

    if not options.reference_file:
        print("Reference file missing.")
        print("")
        argument_parser.print_help()
        print("")
        sys.exit(1)

    writer = CliToolStatWriter()
    result_dict = writer.get_reference_format(sys.stdin)

    with open(options.reference_file, "w", encoding="utf-8") as reference_file_object:
        json_string = json.dumps(result_dict, indent=2, sort_keys=True)
        reference_file_object.write(f"{json_string:s}\n")

    sys.exit(0)
