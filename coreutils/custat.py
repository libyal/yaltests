#!/usr/bin/env python3
"""Parses coreutils stat output.

To create stat output:
    TZ=UTC find mountpoint/ -inum 22 -exec stat --format=${FORMAT} {} + 2>/dev/null

Where FORMAT is:
    '{
        "inode_number": %i,
        "path": "%n",
        "file_mode": "0x%f",
        "number_of_links": %h,
        "user_identifier": %u,
        "group_identifier": %g,
        "number_of_blocks": %b,
        "size": %s,
        "access_time": "%x",
        "modification_time": "%y",
        "creation_time": "%w",
        "change_time": "%z"
    }'
"""

import json
import sys

from datetime import datetime


class StatOutputParser:
    """Parses coreutils stat output."""

    DATE_TIME_ATTRIBUTES = frozenset(
        [
            "access_time",
            "creation_time",
            "change_time",
            "modification_time",
        ]
    )

    HEXADECIMAL_ATTRIBUTES = frozenset(
        [
            "file_mode",
        ]
    )

    def _parse_date_time(self, value: str) -> str:
        """Converts a stat date and time value to ISO 8601.

        Args:
          value (str): date and time value such as
              '2026-07-18 16:46:27.822277576 +0000'.

        Returns:
          str: ISO 8601 formatted date and time value.

        Raises:
          RuntimeError: if the date and time value is not supported.
        """
        if value == "-":
            return None

        value_length = len(value)
        if value_length < 35 or not value.endswith(" +0000"):
            raise RuntimeError(f"Unsupported time value: {value:s}")

        try:
            date_time = datetime.strptime(value[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError as exception:
            raise RuntimeError(
                f"Unable to parse date and time: {value:s}"
            ) from exception

        iso8610_string = date_time.strftime("%Y-%m-%dT%H:%M:%S")
        iso8610_string = "".join([iso8610_string, value[19:-6]])

        return f"{iso8610_string:s}Z"

    def _parse_hexadecimal(self, value: str) -> str:
        """Converts a string of a hexadecimal value into an integer.

        Args:
          value (str): hexadecimal value such as '0xeadbb557'

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

    def parse(self, file_object: IO):
        """Parses coreutils stat.

        Args:
          file_object (file): file-like object containing the stat output.

        Returns:
          dict[str, object]: values parsed from the stat output.

        Raises:
          RuntimeError: if the stat output is not supported.
        """
        file_data = file_object.read()
        if not file_data:
            raise RuntimeError("Missing stat output")

        json_data = json.loads(file_data)

        result = {}

        for key, value in json_data.items():
            if key in self.DATE_TIME_ATTRIBUTES:
                value = self._parse_date_time(value)
            elif key in self.HEXADECIMAL_ATTRIBUTES:
                value = self._parse_hexadecimal(value)

            result[key] = value

        return result


if __name__ == "__main__":
    parser = StatOutputParser()
    result_dict = parser.parse(sys.stdin)
    json_string = json.dumps(result_dict, indent=2)
    print(json_string)
