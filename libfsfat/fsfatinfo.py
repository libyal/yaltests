#!/usr/bin/env python3
"""Parses libfsfat fsfatinfo stat (-E or -F) output.

To create fsfatinfo stat output:
    fsfatinfo -E 35 -o 20480 fatplus.dmg
"""

import json
import re
import sys

from datetime import datetime
from typing import Dict
from typing import IO
from typing import List


class FsFatInfoOutputParser:
    """Parses libfsfat fsfatinfo stat output."""

    _HEADER_RE = re.compile(r"^fsfatinfo (\d+)$")

    FILE_ENTRY_ATTRIBUTE_NAMES = {
        "access time": "access_time",
        "creation time": "creation_time",
        "file attribute flags": "file_attribute_flags",
        "identifier": "identifier",
        "modification time": "modification_time",
        "name": "name",
        "path": "path",
        "size": "size",
    }

    DATE_TIME_ATTRIBUTES = frozenset(
        [
            "access_time",
            "creation_time",
            "modification_time",
        ]
    )

    DECIMAL_ATTRIBUTES = frozenset(
        [
            "size",
        ]
    )

    HEXADECIMAL_ATTRIBUTES = frozenset(
        [
            "file_attribute_flags",
            "identifier",
        ]
    )

    def _parse_date_time(self, value: str) -> str:
        """Converts a fsfatinfo stat date and time value to ISO 8601.

        Args:
          value (str): date and time value such as 'Jul 22, 2021 14:07:32.84'.

        Returns:
          str: ISO 8601 formatted date and time value.

        Raises:
          RuntimeError: if the date and time value is not supported.
        """
        if value == "Not set (0)":
            return None

        value_length = len(value)
        if value_length < 22:
            raise RuntimeError(f"Unsupported time value: {value:s}")

        try:
            date_time = datetime.strptime(value[:21], "%b %d, %Y %H:%M:%S")
        except ValueError as exception:
            raise RuntimeError(
                f"Unable to parse date and time: {value:s}"
            ) from exception

        iso8610_string = date_time.strftime("%Y-%m-%dT%H:%M:%S")
        if value_length > 25:
            iso8610_string = "".join([iso8610_string, value[21:-4]])

        return f"{iso8610_string:s}"

    def _parse_decimal(self, value: str) -> str:
        """Converts a string of a decimal value into an integer.

        Args:
          value (str): decimal value such as '1000'

        Returns:
          int: integer value.

        Raises:
          RuntimeError: if the decimal value is not supported.
        """
        try:
            integer = int(value, 10)
        except ValueError as exception:
            raise RuntimeError("Unable to parse decimal: {value:s}") from exception

        return integer

    def _parse_file_mode(self, file_mode: str) -> int:
        """Converts a file mode string to an octal representation.

        Args:
          file_mode (str): string representation of the file mode, such as
              '-rw-r--r-- (0100644)'.

        Returns:
          int: numeric representation of the file mode.
        """
        try:
            integer = int(file_mode[12:-1], 8)
        except ValueError as exception:
            raise RuntimeError("Unable to octal decimal: {value:s}") from exception

        return integer

    def _parse_header(self, lines: List[str], result: Dict[str, str]):
        """Parse the header.

        Args:
          lines (list[str]): lines of stdout.

        Returns:
          dict[str, object]: metadata.

        Raises:
          RuntimeErrror: if the output is not supported.
        """
        number_of_lines = len(lines)
        if (
            number_of_lines < 2
            or not lines[0].startswith("fsfatinfo ")
            or lines[1].strip() != ""
        ):
            raise RuntimeError("Unsupported fsfatinfo output.")

        match = self._HEADER_RE.search(lines[0])
        if not match:
            raise RuntimeError("Unsupported fsfatinfo header.")

        result["metadata"] = {"version": match.group(1)}

    def _parse_hexadecimal(self, value: str) -> str:
        """Converts a string of a hexadecimal value into an integer.

        Args:
          value (str): hexadecimal value such as '0x1000'

        Returns:
          int: integer value.

        Raises:
          RuntimeError: if the hexadecimal value is not supported.
        """
        try:
            integer = int(value, 16)
        except ValueError as exception:
            raise RuntimeError("Unable to parse hexadecimal: {value:s}") from exception

        return integer

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
            attribute_value = value.strip()

            if attribute_name == "file_mode":
                attribute_value = self._parse_file_mode(attribute_value)
            elif attribute_name in self.DATE_TIME_ATTRIBUTES:
                attribute_value = self._parse_date_time(attribute_value)
            elif attribute_name in self.DECIMAL_ATTRIBUTES:
                attribute_value = self._parse_decimal(attribute_value)
            elif attribute_name in self.HEXADECIMAL_ATTRIBUTES:
                attribute_value = self._parse_hexadecimal(attribute_value)

            result[attribute_name] = attribute_value

        else:
            raise RuntimeError(f"Unsupported line: {line:s}")

    def parse(self, file_object: IO):
        """Parses libfsfat fsfatinfo stat.

        Args:
          file_object (file): file-like object containing the fsfatinfo stat output.

        Returns:
          dict[str, object]: values parsed from the fsfatinfo stat output.

        Raises:
          RuntimeError: if the fsfatinfo stat output is not supported.
        """
        lines = file_object.readlines()
        if not lines:
            raise RuntimeError("Missing fsfatinfo output")

        result = {}

        self._parse_header(lines, result)

        if lines[2] == "File Allocation Table (FAT) file system information:":
            line_index = 4
        else:
            line_index = 2

        if not lines[line_index].startswith("File entry"):
            raise RuntimeError(
                "Unsupported fsfatinfo output - missing file entry section."
            )

        line_index += 1
        section = "file_entry"

        for line in lines[line_index:]:
            line = line.strip()
            if not line:
                if section == "file_attribute_flags":
                    section = "file_entry"
                continue

            if section == "file_entry":
                self._parse_section_file_entry(line, result)

            if line.startswith("File attribute flags"):
                section = "file_attribute_flags"
                continue

        return result


if __name__ == "__main__":
    parser = FsFatInfoOutputParser()
    result_dict = parser.parse(sys.stdin)
    json_string = json.dumps(result_dict, indent=2)
    print(json_string)
