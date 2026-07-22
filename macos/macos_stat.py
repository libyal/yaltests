#!/usr/bin/env python3
"""Parses coreutils stat output.

To create stat output:
    TZ=UTC find mountpoint/ -inum 22 -exec stat --format=${FORMAT} {} + 2>/dev/null

Where FORMAT is:
    '{
        "inode_number": %i,
        "path": "%N",
        "file_mode": "0x%Xp",
        "number_of_links": %l,
        "user_identifier": %u,
        "group_identifier": %g,
        "number_of_blocks": %b,
        "size": %z,
        "access_time": "%Fa",
        "modification_time": "%Fm",
        "creation_time": "%FB",
        "change_time": "%Fc",
    }'
"""

import json
import sys

from datetime import datetime
from datetime import timezone


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
          value (str): date and time value such as '1779328276.000000000'.

        Returns:
          str: ISO 8601 formatted date and time value.

        Raises:
          RuntimeError: if the date and time value is not supported.
        """
        if value == "-":
            return None

        if "." not in value:
            raise RuntimeError(f"Unsupported time value: {value:s}")

        seconds, nanoseconds = value.split(".", maxsplit=1)

        try:
            seconds = int(seconds, 10)
            nanoseconds = int(nanoseconds, 10)
            date_time = datetime.fromtimestamp(seconds, timezone.utc)
        except (TypeError, ValueError) as exception:
            raise RuntimeError(
                f"Unable to parse date and time: {value:s}"
            ) from exception

        iso8610_string = date_time.strftime("%Y-%m-%dT%H:%M:%S")

        return f"{iso8610_string:s}.{nanoseconds:09d}Z"

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
