#!/usr/bin/env python3
"""Parses libfsapfs fsapfsinfo stat (-E or -F) output.

To create fsapfsinfo stat output:
    fsapfsinfo -E 36 -o 20480 apfs_single_volume.dmg
"""

import json
import re
import sys

from datetime import datetime
from typing import Dict
from typing import IO
from typing import List


class FsApfsInfoOutputParser:
    """Parses libfsapfs fsapfsinfo stat output."""

    _HEADER_RE = re.compile(r"^fsapfsinfo (\d+)$")
    _ISO8601_TIME_RE = re.compile(
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
    )

    FILE_ENTRY_ATTRIBUTE_NAMES = {
        "access time": "access_time",
        "added time": "added_time",
        "creation time": "creation_time",
        "device number": "device_number",
        "file mode": "file_mode",
        "group identifier": "group_identifier",
        "identifier": "inode_number",
        "inode change time": "change_time",
        "modification time": "modification_time",
        "name": "name",
        "number of links": "number_of_links",
        "owner identifier": "user_identifier",
        "path": "path",
        "size": "size",
        "symbolic link target": "symbolic_link_target",
    }

    DATE_TIME_ATTRIBUTES = frozenset(
        [
            "access_time",
            "added_time",
            "change_time",
            "creation_time",
            "modification_time",
        ]
    )

    DECIMAL_ATTRIBUTES = frozenset(
        [
            "group_identifier",
            "inode_number",
            "number_of_links",
            "size",
            "user_identifier",
        ]
    )

    def _parse_date_time(self, value: str) -> str:
        """Converts a fsapfsinfo stat date and time value to ISO 8601.

        Args:
          value (str): date and time value such as
              '2026-08-04T11:09:25.297329545Z', 'Jul 22, 2021 14:07:32 UTC', or
              'Jul 22, 2021 14:07:32.841610817 UTC'.

        Returns:
          str: ISO 8601 formatted date and time value.

        Raises:
          RuntimeError: if the date and time value is not supported.
        """
        if value == "Not set (0)":
            return None

        if self._ISO8601_TIME_RE.match(value):
            try:
                datetime.strptime(value[:19], "%Y-%m-%dT%H:%M:%S")
            except ValueError as exception:
                raise RuntimeError(
                    f"Unable to parse date and time: {value:s}"
                ) from exception

            return value

        value_length = len(value)
        if value_length < 25 or not value.endswith(" UTC"):
            raise RuntimeError(f"Unsupported time value: {value:s}")

        try:
            date_time = datetime.strptime(value[:21], "%b %d, %Y %H:%M:%S")
        except ValueError as exception:
            raise RuntimeError(
                f"Unable to parse date and time: {value:s}"
            ) from exception

        iso8601_string = date_time.strftime("%Y-%m-%dT%H:%M:%S")
        if value_length > 25:
            iso8601_string = "".join([iso8601_string, value[21:-4]])

        return f"{iso8601_string:s}Z"

    def _parse_decimal(self, value: str) -> int:
        """Converts a string of a decimal value into an integer.

        Args:
          value (str): decimal value such as '1000'.

        Returns:
          int: integer value.

        Raises:
          RuntimeError: if the decimal value is not supported.
        """
        try:
            integer = int(value, 10)
        except ValueError as exception:
            raise RuntimeError(f"Unable to parse decimal: {value:s}") from exception

        return integer

    def _parse_file_mode(self, file_mode: str) -> int:
        """Converts a file mode string to an octal representation.

        Args:
          file_mode (str): string representation of the file mode, such as
              '-rw-r--r-- (0100644)'.

        Returns:
          int: numeric representation of the file mode.

        Raises:
          RuntimeError: if the file mode value is not supported.
        """
        try:
            integer = int(file_mode[12:-1], 8)
        except ValueError as exception:
            raise RuntimeError(
                f"Unable to parse octal file mode: {file_mode:s}"
            ) from exception

        return integer

    def _parse_header(self, lines: List[str], result: Dict[str, str]):
        """Parse the header.

        Args:
          lines (list[str]): lines of stdout.
          result (dict[str, object]): resulting attributes.

        Raises:
          RuntimeError: if the output is not supported.
        """
        number_of_lines = len(lines)
        if (
            number_of_lines < 2
            or not lines[0].startswith("fsapfsinfo ")
            or lines[1].strip() != ""
        ):
            raise RuntimeError("Unsupported fsapfsinfo output.")

        match = self._HEADER_RE.search(lines[0])
        if not match:
            raise RuntimeError("Unsupported fsapfsinfo header.")

        result["metadata"] = {"version": match.group(1)}

    def _parse_section_file_entry(self, line: str, result: Dict[str, str]):
        """Parses a line of the file entry section.

        Args:
          line (str): line in the section.
          result (dict): resulting attributes.

        Raises:
          RuntimeError: if the line is not supported.
        """
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip().lower()

            attribute_name = self.FILE_ENTRY_ATTRIBUTE_NAMES.get(key)
            if not attribute_name:
                raise RuntimeError(f"Unsupported key: {key:s}")

            attribute_value = value.strip()

            if attribute_name == "file_mode":
                attribute_value = self._parse_file_mode(attribute_value)
            elif attribute_name in self.DATE_TIME_ATTRIBUTES:
                attribute_value = self._parse_date_time(attribute_value)
            elif attribute_name in self.DECIMAL_ATTRIBUTES:
                attribute_value = self._parse_decimal(attribute_value)

            result[attribute_name] = attribute_value

        else:
            raise RuntimeError(f"Unsupported line: {line:s}")

    def parse(self, file_object: IO):
        """Parses libfsapfs fsapfsinfo stat.

        Args:
          file_object (file): file-like object containing the fsapfsinfo stat output.

        Returns:
          dict[str, object]: values parsed from the fsapfsinfo stat output.

        Raises:
          RuntimeError: if the fsapfsinfo stat output is not supported.
        """
        lines = file_object.readlines()
        if not lines:
            raise RuntimeError("Missing fsapfsinfo output")

        result = {}

        self._parse_header(lines, result)

        if (
            len(lines) > 4
            and lines[2].strip() == "Apple File System (APFS) information:"
        ):
            line_index = 4
        else:
            line_index = 2

        if line_index >= len(lines) or not lines[line_index].startswith("File entry"):
            raise RuntimeError(
                "Unsupported fsapfsinfo output - missing file entry section."
            )

        line_index += 1
        section = "file_entry"

        for line in lines[line_index:]:
            line = line.strip()
            if not line:
                continue

            if line.startswith("Extended attributes:"):
                section = "extended_attributes"
                continue

            if section == "file_entry":
                self._parse_section_file_entry(line, result)

        return result


if __name__ == "__main__":
    parser = FsApfsInfoOutputParser()
    result_dict = parser.parse(sys.stdin)
    json_string = json.dumps(result_dict, indent=2)
    print(json_string)
